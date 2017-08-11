#!/usr/bin/env perl

use strict;
use warnings;
use autodie;
use English qw( -no_match_vars );
use utf8;
use 5.010;

use version; our $VERSION = qv('0.2.0');

my $service   = shift();
my $operation = shift();

if (defined $service) {
    if ( $service !~ /\.service$/xms ) {
        $service .= '.service';
    }
    $operation //= 'status';
    exec('systemctl', $operation, $service);
} else {
    $operation //= 'list-units';
    exec('systemctl', $operation);
}
