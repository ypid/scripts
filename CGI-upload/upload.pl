#!/usr/bin/perl
use strict;
use warnings;
use utf8;
use CGI;
$CGI::POST_MAX = 1024 * 1024 * 1024 * 5; ## Maximalgröße einer Datei ist 5GB
use CGI::Carp qw(fatalsToBrowser);
use Digest::MD5;
use Digest::SHA;

my $cgi = CGI->new();
print $cgi->header( -type => 'text/html' );
print $cgi->start_html( -title => 'Perl Skript für das Hochladen von Dateien' );

my %params     = $cgi->Vars();
my $path       = '/home/internet/uploads';
my $filehandle = $cgi->upload('datei');
my $filename   = $params{'datei'};

unless ($filename) {
    print "Bitte wählen Sie ihre Datei auf "
      . $cgi->a( { -href => "index.html" }, "dieser Seite" ) . " aus."
      . $cgi->end_html();
    exit 1;
}

my $user_agent = $ENV{HTTP_USER_AGENT};
$filename = ( split( /[\\\/]/, $filename ) )[-1];
$filename   =~ s/[^A-Za-z0-9_\.\-]//g;
$user_agent =~ s#/#-#g;
$user_agent =~ s# #_#g;
$path .= "/$user_agent/$ENV{REMOTE_ADDR}";
mkdir $path;

upload_file( $filename, $filehandle );
print "<br>\n" . $cgi->a( { -href => "index.html" }, "Weitere Datei hochladen" ) . $cgi->end_html();

sub upload_file {
    my ( $filename, $filehandle ) = @_;
    my $target = $path . '/' . $filename;
    if ( -e $target ) {
        print "Zieldatei existiert schon!";
        exit 0;
    }
    else {
        binmode $filehandle;
        open my $target_fh, '>', $target or die $!;
        binmode $target_fh;
        my $buffer;
        my $ctx = Digest::MD5->new;
        my $sha = Digest::SHA->new('sha256');
        while ( read $filehandle, $buffer, 1024 ) {
            print {$target_fh} $buffer;
            $ctx->add($buffer);
            $sha->add($buffer);
        }
        close $target_fh;
        print $cgi->h2("Ihre Datei wurde als $filename gespeichert"),
          "\nDie Datei ist " . ( stat($target) )[7] . " Byte gro&szlig;<br>",
          "\nDie MD5-Summe lautet: ",
          $ctx->hexdigest,
          "<br>\nDie SHA-256-Summe lautet: ",
          $sha->hexdigest;
    } ## end else [ if ( -e $target ) ]
} ## end sub upload_file