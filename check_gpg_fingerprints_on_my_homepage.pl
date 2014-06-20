#!/usr/bin/env perl
use strict;
use warnings;
use autodie;
use feature qw(say);
use utf8;
use open qw(:std :utf8);
binmode STDOUT, ':encoding(UTF-8)';

my %PAGES_WITH_GPG_KEYS=( 'blog' => 'ypid.wordpress.com/uber-mich',
    'osm-wiki'=>'wiki.openstreetmap.org/wiki/User:Ypid');
my @PROTOCOLS=qw( http https )
