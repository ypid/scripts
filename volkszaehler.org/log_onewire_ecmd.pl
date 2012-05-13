#!/usr/bin/perl -w
#Auslesen der 1 Wire Temperatursensoren vom Typ DS18S20(+) an einem AVR-NET-IO mit ethersex und Datenübertragung zum Volkszaehler
# */1 * * * * /usr/local/bin/vz/1wVZ.pl >>/var/log/1wVZ.log 2>&1

use strict;
#use diagnostics;
use 5.010;
use Net::Telnet ();
require LWP::UserAgent;
use HTTP::Request::Common;

#configuration start
my $esexip   = "192.168.0.230";			#ip or hostname for ethersex
my $esexport = "2701";				#ECMD port
my $url      = "http://127.0.0.1/volkszaehler/middleware.php"; #url to volkszaehler middleware
my $uname    = "<username>";			#username for basic-auth from apache
my $password = "<password>";			#password
my $timeout  = 10;				#timeout for all in seconds
my $debug    = $ENV{debug} // 0;
# 0: normally no output 
# 1: only sensor values
# 2: all

#Temperature Sensors
my @DS18S20 = (
	[ '10127f390208002e', '5598a6c0-2432-11e1-9389-d942d4c87e54', 'TemperaturSensor' ],
#	[ '', '', '' ],
);
#configuration end

my ($esex, @sensor, $sensor, $dummy, $temp);

$esex = Net::Telnet->new || die "fail with Net::Telnet";
$esex->open(
	Host	=> $esexip,
	Port	=> $esexport,
	Timeout	=> $timeout
);
#print localtime() . " Ethersex connected\n";

#Alle Sensor-IDs auslesen und dem Array @sensor zuweisen
$esex->print("1w list");
($sensor) = $esex->waitfor(
	Timeout	=> $timeout,
	String	=> "OK"
);
@sensor = split( /\s+/, $sensor );
#print localtime() . " DS18S20_IDs: @sensor\n";

my $zahler = @sensor;
die "Keine Sensoren Verfügbar" if $zahler == 0;
print "Anzahl der Sensoren: $zahler\n" if $debug >= 2;

#Alle Sensor Temperaturen einlesen
foreach (@sensor) {
	$esex->print("1w convert $_");
	$esex->waitfor(
		Timeout => $timeout,
		String  => "OK"
	);
	print "Sensor $_ done\n" if $debug >= 2;
}
print localtime() . " Temperature conversation done\n" if $debug >= 2;

#Sensor ID inklusive Wert ausgeben und zum Volkszaehler uebermitteln
my $familiar;	## Benutzt um zu testen ob der Sensor schon in @DS18S20 ist
print "-" x 81 . "\n" if $debug >= 1;
foreach (@sensor) {
	$esex->print("1w get $_");
	( $dummy, $temp ) = $esex->waitfor(
		Match   => '/[-]?\d+\.\d+/',
		Timeout => $timeout
	);
	if ($temp == 85) {
		print localtime() . " Temperature out of range $_: $temp\n" if $debug <= 0;
		next;
	}

	foreach my $ref (@DS18S20) {
		if ( @$ref[0] eq $_ ) {
			print "ID_DS18S20: " . @$ref[0] . " Temp: " . $temp . "°C "
				. "uuid: " . @$ref[1] . " Name: @$ref[2]\n" if $debug >= 1;
			$familiar = 1;

			if (1) {
			my $h = HTTP::Headers->new;
			my $reqString =
				$url
			  . '/data/'
			  . @$ref[1]
			  . '.json?value='
			  . $temp;

			my $ua = LWP::UserAgent->new;
			$h->authorization_basic( $uname, $password );

			my $r = HTTP::Request->new( 'POST', $reqString, $h );

			my $response = $ua->request($r);
			print "Server response: " . $response->content . "\n" if $debug >= 1;
			}
			last;

		} else {
			$familiar = 0;
		}
	}
	print "ID_DS18S20: $_ Temp: ${temp}°C uuid: Noch nicht vorhanden!!!\n" if $familiar == 0;
}
print "*" x 81 . "\n" if $debug >= 1;
