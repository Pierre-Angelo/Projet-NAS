# ProjetGNS3-grp19
Projet Routage Réseaux

Plan d'addressage : Réseaux simple

	AS 111 : RIP + iBGP
	 	R11 : 
			l0  1::1
			2/0 111:1::1
		R12 : 
			l0  1::2
			2/0 111:1::2
			1/0 111:2::2

		R13 : 
			l0  1::3
			2/0 111:2::1
			1/0 333:1::1 


	AS 222 : OSPF + iBGP
	 	R21 : 
			l0  2::1
			2/0 222:1::1
		R22 : 
			l0  2::2
			1/0 222:1::2
			3/0 222:2::2
		R23 : 
			l0  2::3
			3/0 222:2::1
			1/0 333:1::2 
	eBGP entre les 2 AS configuré sur leurs interfaces physiques. Ping seulement entre l0 R13 et R23 (en plus du lien local)

			
			


