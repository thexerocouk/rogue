#!/usr/bin/python3

freeradius_eap_all = '''
	md5 {
	}

	#
	# EAP-pwd -- secure password-based authentication
	#
	pwd {
		group = 19

		#
		server_id = theserver@example.com

		#  This has the same meaning as for TLS.
		fragment_size = 1020

		# The virtual server which determines the
		# "known good" password for the user.
		# Note that unlike TLS, only the "authorize"
		# section is processed.  EAP-PWD requests can be
		# distinguished by having a User-Name, but
		# no User-Password, CHAP-Password, EAP-Message, etc.
		virtual_server = "inner-tunnel"
	}

	# Cisco LEAP
	#
	#  We do not recommend using LEAP in new deployments.  See:
	#  http://www.securiteam.com/tools/5TP012ACKE.html
	#
	#  Cisco LEAP uses the MS-CHAP algorithm (but not
	#  the MS-CHAP attributes) to perform it's authentication.
	#
	#  As a result, LEAP *requires* access to the plain-text
	#  User-Password, or the NT-Password attributes.
	#  'System' authentication is impossible with LEAP.
	#
	leap {
	}

	#  Generic Token Card.
	#
	#  Currently, this is only permitted inside of EAP-TTLS,
	#  or EAP-PEAP.  The module "challenges" the user with
	#  text, and the response from the user is taken to be
	#  the User-Password.
	#
	#  Proxying the tunneled EAP-GTC session is a bad idea,
	#  the users password will go over the wire in plain-text,
	#  for anyone to see.
	#
	gtc {
		#  The default challenge, which many clients
		#  ignore..
		#challenge = "Password: "

		#  The plain-text response which comes back
		#  is put into a User-Password attribute,
		#  and passed to another module for
		#  authentication.  This allows the EAP-GTC
		#  response to be checked against plain-text,
		#  or crypt'd passwords.
		#
		#  If you say "Local" instead of "PAP", then
		#  the module will look for a User-Password
		#  configured for the request, and do the
		#  authentication itself.
		#
		auth_type = PAP
	}

	## Common TLS configuration for TLS-based EAP types
	#
	#  See raddb/certs/README for additional comments
	#  on certificates.
	#
	#  If OpenSSL was not found at the time the server was
	#  built, the "tls", "ttls", and "peap" sections will
	#  be ignored.
	#
	#  If you do not currently have certificates signed by
	#  a trusted CA you may use the 'snakeoil' certificates.
	#  Included with the server in raddb/certs.
	#
	#  If these certificates have not been auto-generated:
	#    cd raddb/certs
	#    make
	#
	#  These test certificates SHOULD NOT be used in a normal
	#  deployment.  They are created only to make it easier
	#  to install the server, and to perform some simple
	#  tests with EAP-TLS, TTLS, or PEAP.
	#
	#  See also:
	#
	#  http://www.dslreports.com/forum/remark,9286052~mode=flat
	#
	#  Note that you should NOT use a globally known CA here!
	#  e.g. using a Verisign cert as a "known CA" means that
	#  ANYONE who has a certificate signed by them can
	#  authenticate via EAP-TLS!  This is likely not what you want.
	tls-config tls-common {
		private_key_password = %s
		private_key_file = %s

		#  If Private key & Certificate are located in
		#  the same file, then private_key_file &
		#  certificate_file must contain the same file
		#  name.
		#
		#  If ca_file (below) is not used, then the
		#  certificate_file below MUST include not
		#  only the server certificate, but ALSO all
		#  of the CA certificates used to sign the
		#  server certificate.
		certificate_file = %s

		#  Trusted Root CA list
		#
		#  ALL of the CA's in this list will be trusted
		#  to issue client certificates for authentication.
		#
		#  In general, you should use self-signed
		#  certificates for 802.1x (EAP) authentication.
		#  In that case, this CA file should contain
		#  *one* CA certificate.
		#
		ca_file = %s

	 	#  OpenSSL will automatically create certificate chains,
	 	#  unless we tell it to not do that.  The problem is that
	 	#  it sometimes gets the chains right from a certificate
	 	#  signature view, but wrong from the clients view.
		#
		#  When setting "auto_chain = no", the server certificate
		#  file MUST include the full certificate chain.
	#	auto_chain = yes

		#
		#  If OpenSSL supports TLS-PSK, then we can use
		#  a PSK identity and (hex) password.  When the
		#  following two configuration items are specified,
		#  then certificate-based configuration items are
		#  not allowed.  e.g.:
		#
		#	private_key_password
		#	private_key_file
		#	certificate_file
		#	ca_file
		#	ca_path
		#
		#  For now, the identity is fixed, and must be the
		#  same on the client.  The passphrase must be a hex
		#  value, and can be up to 256 hex digits.
		#
		#  Future versions of the server may be able to
		#  look up the shared key (hexphrase) based on the
		#  identity.
		#
	#	psk_identity = "test"
	#	psk_hexphrase = "036363823"

		#
		#  For DH cipher suites to work, you have to
		#  run OpenSSL to create the DH file first:
		#
		#  	openssl dhparam -out certs/dh 2048
		#
		dh_file = %s

		#
		#  If your system doesn't have /dev/urandom,
		#  you will need to create this file, and
		#  periodically change its contents.
		#
		#  For security reasons, FreeRADIUS doesn't
		#  write to files in its configuration
		#  directory.
		#
	#	random_file = /dev/urandom

		#
		#  This can never exceed the size of a RADIUS
		#  packet (4096 bytes), and is preferably half
		#  that, to accommodate other attributes in
		#  RADIUS packet.  On most APs the MAX packet
		#  length is configured between 1500 - 1600
		#  In these cases, fragment size should be
		#  1024 or less.
		#
	#	fragment_size = 1024

		#  include_length is a flag which is
		#  by default set to yes If set to
		#  yes, Total Length of the message is
		#  included in EVERY packet we send.
		#  If set to no, Total Length of the
		#  message is included ONLY in the
		#  First packet of a fragment series.
		#
	#	include_length = yes


		#  Check the Certificate Revocation List
		#
		#  1) Copy CA certificates and CRLs to same directory.
		#  2) Execute 'c_rehash <CA certs&CRLs Directory>'.
		#    'c_rehash' is OpenSSL's command.
		#  3) uncomment the lines below.
		#  5) Restart radiusd
	#	check_crl = yes

		# Check if intermediate CAs have been revoked.
	#	check_all_crl = yes

		ca_path = %s

		#
		#  If check_cert_issuer is set, the value will
		#  be checked against the DN of the issuer in
		#  the client certificate.  If the values do not
		#  match, the certificate verification will fail,
		#  rejecting the user.
		#
		#  In 2.1.10 and later, this check can be done
		#  more generally by checking the value of the
		#  TLS-Client-Cert-Issuer attribute.  This check
		#  can be done via any mechanism you choose.
		#
	#	check_cert_issuer = "/C=GB/ST=Berkshire/L=Newbury/O=My Company Ltd"

		#
		#  If check_cert_cn is set, the value will
		#  be xlat'ed and checked against the CN
		#  in the client certificate.  If the values
		#  do not match, the certificate verification
		#  will fail rejecting the user.
		#
		#  This check is done only if the previous
		#  "check_cert_issuer" is not set, or if
		#  the check succeeds.
		#
		#  In 2.1.10 and later, this check can be done
		#  more generally by checking the value of the
		#  TLS-Client-Cert-CN attribute.  This check
		#  can be done via any mechanism you choose.
		#
	#	check_cert_cn = [[User-Name]]
		#
		# Set this option to specify the allowed
		# TLS cipher suites.  The format is listed
		# in "man 1 ciphers".
		#
		# For EAP-FAST, use "ALL:!EXPORT:!eNULL:!SSLv2"
		#
		cipher_list = "DEFAULT"

		# If enabled, OpenSSL will use server cipher list
		# (possibly defined by cipher_list option above)
		# for choosing right cipher suite rather than
		# using client-specified list which is OpenSSl default
		# behavior. Having it set to yes is a current best practice
		# for TLS
		cipher_server_preference = no

		# Work-arounds for OpenSSL nonsense
		# OpenSSL 1.0.1f and 1.0.1g do not calculate
		# the EAP keys correctly.  The fix is to upgrade
		# OpenSSL, or disable TLS 1.2 here. 
		#
		#  For EAP-FAST, this MUST be set to "yes".
		#
#		disable_tlsv1_2 = no

		#

		#
		#  Elliptical cryptography configuration
		#
		#  Only for OpenSSL >= 0.9.8.f
		#
		ecdh_curve = "prime256v1"

		#
		#  Session resumption / fast reauthentication
		#  cache.
		#
		#  The cache contains the following information:
		#
		#  session Id - unique identifier, managed by SSL
		#  User-Name  - from the Access-Accept
		#  Stripped-User-Name - from the Access-Request
		#  Cached-Session-Policy - from the Access-Accept
		#
		#  The "Cached-Session-Policy" is the name of a
		#  policy which should be applied to the cached
		#  session.  This policy can be used to assign
		#  VLANs, IP addresses, etc.  It serves as a useful
		#  way to re-apply the policy from the original
		#  Access-Accept to the subsequent Access-Accept
		#  for the cached session.
		#
		#  On session resumption, these attributes are
		#  copied from the cache, and placed into the
		#  reply list.
		#
		#  You probably also want "use_tunneled_reply = yes"
		#  when using fast session resumption.
		#
		cache {
			#
			#  Enable it.  The default is "no". Deleting the entire "cache"
			#  subsection also disables caching.
			#
			#  You can disallow resumption for a particular user by adding the
			#  following attribute to the control item list:
			#
			#    Allow-Session-Resumption = No
			#
			#  If "enable = no" below, you CANNOT enable resumption for just one
			#  user by setting the above attribute to "yes".
			#
			enable = yes

			#
			#  Lifetime of the cached entries, in hours. The sessions will be
			#  deleted/invalidated after this time.
			#
			lifetime = 24 # hours

			#
			#  The maximum number of entries in the
			#  cache.  Set to "0" for "infinite".
			#
			#  This could be set to the number of users
			#  who are logged in... which can be a LOT.
			#
			max_entries = 255

			#
			#  Internal "name" of the session cache. Used to
			#  distinguish which TLS context sessions belong to.
			#
			#  The server will generate a random value if unset.
			#  This will change across server restart so you MUST
			#  set the "name" if you want to persist sessions (see
			#  below).
			#
			#name = "EAP module"

			#
			#  Simple directory-based storage of sessions.
			#  Two files per session will be written, the SSL
			#  state and the cached VPs. This will persist session
			#  across server restarts.
			#
			#  The server will need write perms, and the directory
			#  should be secured from anyone else. You might want
			#  a script to remove old files from here periodically:
			#
			#
			#  This feature REQUIRES "name" option be set above.
			#
			#persist_dir = "/var/log/freeradius-wpe/tlscache"
		}

		#
		#  As of version 2.1.10, client certificates can be
		#  validated via an external command.  This allows
		#  dynamic CRLs or OCSP to be used.
		#
		#  This configuration is commented out in the
		#  default configuration.  Uncomment it, and configure
		#  the correct paths below to enable it.
		#
		#  If OCSP checking is enabled, and the OCSP checks fail,
		#  the verify section is not run.
		#
		#  If OCSP checking is disabled, the verify section is
		#  run on successful certificate validation.
		#
		verify {
			#  If the OCSP checks succeed, the verify section
			#  is run to allow additional checks.
			#
			#  If you want to skip verify on OCSP success,
			#  uncomment this configuration item, and set it
			#  to "yes".
	#		skip_if_ocsp_ok = no

			#  A temporary directory where the client
			#  certificates are stored.  This directory
			#  MUST be owned by the UID of the server,
			#  and MUST not be accessible by any other
			#  users.  When the server starts, it will do
			#  "chmod go-rwx" on the directory, for
			#  security reasons.  The directory MUST
			#  exist when the server starts.
			#
			#  You should also delete all of the files
			#  in the directory when the server starts.
	#		tmpdir = /tmp/radiusd

			#  The command used to verify the client cert.
			#  We recommend using the OpenSSL command-line
			#  tool.
			#
			#  The ca_path text is a reference to
			#  the ca_path variable defined above.
			#
			#  The [[TLS-Client-Cert-Filename]] is the name
			#  of the temporary file containing the cert
			#  in PEM format.  This file is automatically
			#  deleted by the server when the command
			#  returns.
	#		client = "/path/to/openssl verify -CApath /etc/freeradius-wpe/3.0/certs [[TLS-Client-Cert-Filename]]"
		}

		#
		#  OCSP Configuration
		#  Certificates can be verified against an OCSP
		#  Responder. This makes it possible to immediately
		#  revoke certificates without the distribution of
		#  new Certificate Revocation Lists (CRLs).
		#
		ocsp {
			#
			#  Enable it.  The default is "no".
			#  Deleting the entire "ocsp" subsection
			#  also disables ocsp checking
			#
			enable = no

			#
			#  The OCSP Responder URL can be automatically
			#  extracted from the certificate in question.
			#  To override the OCSP Responder URL set
			#  "override_cert_url = yes".
			#
			override_cert_url = yes

			#
			#  If the OCSP Responder address is not extracted from
			#  the certificate, the URL can be defined here.
			#
			url = "http://127.0.0.1/ocsp/"

			#
			# If the OCSP Responder can not cope with nonce
			# in the request, then it can be disabled here.
			#
			# For security reasons, disabling this option
			# is not recommended as nonce protects against
			# replay attacks.
			#
			# Note that Microsoft AD Certificate Services OCSP
			# Responder does not enable nonce by default. It is
			# more secure to enable nonce on the responder than
			# to disable it in the query here.
			#
			# use_nonce = yes

			#
			# Number of seconds before giving up waiting
			# for OCSP response. 0 uses system default.
			#
			# timeout = 0

			#
			# Normally an error in querying the OCSP
			# responder (no response from server, server did
			# not understand the request, etc) will result in
			# a validation failure.
			#
			# To treat these errors as 'soft' failures and
			# still accept the certificate, enable this
			# option.
			#
			# Warning: this may enable clients with revoked
			# certificates to connect if the OCSP responder
			# is not available. Use with caution.
			#
			# softfail = no
		}
	}

	## EAP-TLS
	#
	#  As of Version 3.0, the TLS configuration for TLS-based
	#  EAP types is above in the "tls-config" section.
	#
	tls {
		# Point to the common TLS configuration
		tls = tls-common

		#
		# As part of checking a client certificate, the EAP-TLS
		# sets some attributes such as TLS-Client-Cert-CN. This
		# virtual server has access to these attributes, and can
		# be used to accept or reject the request.
		#
	#	virtual_server = check-eap-tls
	}


	## EAP-TTLS
	#
	#  The TTLS module implements the EAP-TTLS protocol,
	#  which can be described as EAP inside of Diameter,
	#  inside of TLS, inside of EAP, inside of RADIUS...
	#
	#  Surprisingly, it works quite well.
	#
	ttls {
		#  Which tls-config section the TLS negotiation parameters
		#  are in - see EAP-TLS above for an explanation.
		#
		#  In the case that an old configuration from FreeRADIUS
		#  v2.x is being used, all the options of the tls-config
		#  section may also appear instead in the 'tls' section
		#  above. If that is done, the tls= option here (and in
		#  tls above) MUST be commented out.
		#
		tls = tls-common

		#  The tunneled EAP session needs a default EAP type
		#  which is separate from the one for the non-tunneled
		#  EAP module.  Inside of the TTLS tunnel, we recommend
		#  using EAP-MD5.  If the request does not contain an
		#  EAP conversation, then this configuration entry is
		#  ignored.
		#
		default_eap_type = md5

		#  The tunneled authentication request does not usually
		#  contain useful attributes like 'Calling-Station-Id',
		#  etc.  These attributes are outside of the tunnel,
		#  and normally unavailable to the tunneled
		#  authentication request.
		#
		#  By setting this configuration entry to 'yes',
		#  any attribute which is NOT in the tunneled
		#  authentication request, but which IS available
		#  outside of the tunnel, is copied to the tunneled
		#  request.
		#
		#  allowed values: {no, yes}
		#
		copy_request_to_tunnel = no

		#
		#  As of version 3.0.5, this configuration item
		#  is deprecated.  Instead, you should use
		#
		# 	update outer.session-state {
		#		...
		#
		#	}
		#
		#  This will cache attributes for the final Access-Accept.
		#
		#  The reply attributes sent to the NAS are usually
		#  based on the name of the user 'outside' of the
		#  tunnel (usually 'anonymous').  If you want to send
		#  the reply attributes based on the user name inside
		#  of the tunnel, then set this configuration entry to
		#  'yes', and the reply to the NAS will be taken from
		#  the reply to the tunneled request.
		#
		#  allowed values: {no, yes}
		#
		use_tunneled_reply = no

		#
		#  The inner tunneled request can be sent
		#  through a virtual server constructed
		#  specifically for this purpose.
		#
		#  If this entry is commented out, the inner
		#  tunneled request will be sent through
		#  the virtual server that processed the
		#  outer requests.
		#
		virtual_server = "inner-tunnel"

		#  This has the same meaning, and overwrites, the
		#  same field in the "tls" configuration, above.
		#  The default value here is "yes".
		#
	#	include_length = yes

		#
		# Unlike EAP-TLS, EAP-TTLS does not require a client
		# certificate. However, you can require one by setting the
		# following option. You can also override this option by
		# setting
		#
		#	EAP-TLS-Require-Client-Cert = Yes
		#
		# in the control items for a request.
		#
	#	require_client_cert = yes
	}


	## EAP-PEAP
	#

	##################################################
	#
	#  !!!!! WARNINGS for Windows compatibility  !!!!!
	#
	##################################################
	#
	#  If you see the server send an Access-Challenge,
	#  and the client never sends another Access-Request,
	#  then
	#
	#		STOP!
	#
	#  The server certificate has to have special OID's
	#  in it, or else the Microsoft clients will silently
	#  fail.  See the "scripts/xpextensions" file for
	#  details, and the following page:
	#
	#	http://support.microsoft.com/kb/814394/en-us
	#
	#  For additional Windows XP SP2 issues, see:
	#
	#	http://support.microsoft.com/kb/885453/en-us
	#
	#
	#  If is still doesn't work, and you're using Samba,
	#  you may be encountering a Samba bug.  See:
	#
	#	https://bugzilla.samba.org/show_bug.cgi?id=6563
	#
	#  Note that we do not necessarily agree with their
	#  explanation... but the fix does appear to work.
	#
	##################################################

	#
	#  The tunneled EAP session needs a default EAP type
	#  which is separate from the one for the non-tunneled
	#  EAP module.  Inside of the TLS/PEAP tunnel, we
	#  recommend using EAP-MS-CHAPv2.
	#
	peap {
		#  Which tls-config section the TLS negotiation parameters
		#  are in - see EAP-TLS above for an explanation.
		#
		#  In the case that an old configuration from FreeRADIUS
		#  v2.x is being used, all the options of the tls-config
		#  section may also appear instead in the 'tls' section
		#  above. If that is done, the tls= option here (and in
		#  tls above) MUST be commented out.
		#
		tls = tls-common

		#  The tunneled EAP session needs a default
		#  EAP type which is separate from the one for
		#  the non-tunneled EAP module.  Inside of the
		#  PEAP tunnel, we recommend using MS-CHAPv2,
		#  as that is the default type supported by
		#  Windows clients.
		#
		default_eap_type = mschapv2

		#  The PEAP module also has these configuration
		#  items, which are the same as for TTLS.
		#
		copy_request_to_tunnel = no

		#
		#  As of version 3.0.5, this configuration item
		#  is deprecated.  Instead, you should use
		#
		# 	update outer.session-state {
		#		...
		#
		#	}
		#
		#  This will cache attributes for the final Access-Accept.
		#
		use_tunneled_reply = no

		#  When the tunneled session is proxied, the
		#  home server may not understand EAP-MSCHAP-V2.
		#  Set this entry to "no" to proxy the tunneled
		#  EAP-MSCHAP-V2 as normal MSCHAPv2.
		#
	#	proxy_tunneled_request_as_eap = yes

		#
		#  The inner tunneled request can be sent
		#  through a virtual server constructed
		#  specifically for this purpose.
		#
		#  If this entry is commented out, the inner
		#  tunneled request will be sent through
		#  the virtual server that processed the
		#  outer requests.
		#
		virtual_server = "inner-tunnel"

		# This option enables support for MS-SoH
		# see doc/SoH.txt for more info.
		# It is disabled by default.
		#
	#	soh = yes

		#
		# The SoH reply will be turned into a request which
		# can be sent to a specific virtual server:
		#
	#	soh_virtual_server = "soh-server"

		#
		# Unlike EAP-TLS, PEAP does not require a client certificate.
		# However, you can require one by setting the following
		# option. You can also override this option by setting
		#
		#	EAP-TLS-Require-Client-Cert = Yes
		#
		# in the control items for a request.
		#
	#	require_client_cert = yes
	}

	#
	#  This takes no configuration.
	#
	#  Note that it is the EAP MS-CHAPv2 sub-module, not
	#  the main 'mschap' module.
	#
	#  Note also that in order for this sub-module to work,
	#  the main 'mschap' module MUST ALSO be configured.
	#
	#  This module is the *Microsoft* implementation of MS-CHAPv2
	#  in EAP.  There is another (incompatible) implementation
	#  of MS-CHAPv2 in EAP by Cisco, which FreeRADIUS does not
	#  currently support.
	#
	mschapv2 {
		#  Prior to version 2.1.11, the module never
		#  sent the MS-CHAP-Error message to the
		#  client.  This worked, but it had issues
		#  when the cached password was wrong.  The
		#  server *should* send "E=691 R=0" to the
		#  client, which tells it to prompt the user
		#  for a new password.
		#
		#  The default is to behave as in 2.1.10 and
		#  earlier, which is known to work.  If you
		#  set "send_error = yes", then the error
		#  message will be sent back to the client.
		#  This *may* help some clients work better,
		#  but *may* also cause other clients to stop
		#  working.
		#
#		send_error = no

		#  Server identifier to send back in the challenge.
		#  This should generally be the host name of the
		#  RADIUS server.  Or, some information to uniquely
		#  identify it.
#		identity = "FreeRADIUS"
	}

	## EAP-FAST
	#
	#  The FAST module implements the EAP-FAST protocol
	#
	fast {
		# Point to the common TLS configuration
		#
		# cipher_list though must include "ADH" for anonymous provisioning.
		# This is not as straight forward as appending "ADH" alongside
		# "DEFAULT" as "DEFAULT" contains "!aNULL" so instead it is
		# recommended "ALL:!EXPORT:!eNULL:!SSLv2" is used
		#
		tls = tls-common

		# PAC lifetime in seconds (default: seven days)
		#
		pac_lifetime = 604800

		# Authority ID of the server
		#
		# if you are running a cluster of RADIUS servers, you should make
		# the value chosen here (and for "pac_opaque_key") the same on all
		# your RADIUS servers.  This value should be unique to your
		# installation.  We suggest using a domain name.
		#
		authority_identity = "1234"

		# PAC Opaque encryption key (must be exactly 32 bytes in size)
		#
		# This value MUST be secret, and MUST be generated using
		# a secure method, such as via 'openssl rand -hex 32'
		#
		pac_opaque_key = "0123456789abcdef0123456789ABCDEF"

		# Same as for TTLS, PEAP, etc.
		#
		virtual_server = inner-tunnel
	}

'''
