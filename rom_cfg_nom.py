
nom_aliases = """
%%alias Case,Gender,Number CGN 
%%alias Case,Gender,Number,lemma CGNL
%%alias Case,Gender,Number,Person,lemma CGNPL
%%alias lemma L
"""

det_cfg = """
DetP[CGNL=@] ::= DET[CGNL=@]
DetP[CGNL=@] ::= QP[CGNL=@]
DetP[CGNL=@] ::= DET[CGNL=@] QP[CGNL=@]
"""

num_cfg = """
QP[CGNL=@] ::= NUM[CGNL=@]
"""

adj_cfg = """
AdjP[CGNL=@] ::= ADJ[CGNL=@]
AdjP[CGNL=@] ::= GV[CGNL=@ VerbForm=Part]
AdjP[CGNL=@] ::= AdvP AdjP[CGNL=@]
AdjP[CGN=@ L=@] ::= AdjP[CGN=@] AdjPConj[CGNL=@]
AdjPConj[CGN=@ L=@] ::= CCONJ[L=@] AdjP[CGN=@] 
"""

noun_cfg = """
N0[CGNPL=@ det=T Person=3] ::= DetP[CGN=@] N0[CGNL=@ det=F]
N0[CGNPL=@] ::= PRON[CGNPL=@]
N0[CGNPL=@] ::= PROPN[CGNPL=@]
N0[CGNL=@ Person=3] ::= NOUN[CGNL=@]
N0[CGNL=@ Person=3] ::= AdjP[CGN=@] NOUN[CGNL=@]
N0[CGNL=@ Person=3] ::= NOUN[CGNL=@] QP


NP[CGNPL=@] ::= N0[CGNPL=@]
NP[CGNPL=@] ::= NP[CGNPL=@] AdjP[CGN=@]
%reverse
NP[CGNPL=@] ::= NP[CGNPL=@] NP[Case=Gen]
%reverse
NP[CGNPL=@] ::= NP[CGNPL=@] PP
NP[CGNPL=@] ::= NP[CGNPL=@] NP[Case=Nom]
"""

adv_cfg = """
AdvP ::= ADV
"""

pp_cfg = """
PREP[Case=@] ::= ADP[Case=@]
PREP[Case=@] ::= PREP ADP[Case=@]
PP ::= PREP[Case=@] NP[Case=@]
"""

cfg_list = [nom_aliases, det_cfg, num_cfg, adj_cfg, noun_cfg, adv_cfg, pp_cfg]
