
nom_aliases = """
%%alias Case,Gender,Number CGN 
%%alias Case,Gender,Number,lemma CGNL 
%%alias lemma L
"""

det_cfg = """
DetP ::= h:DET
DetP ::= h:QP
DetP[CGN=@] ::= h:DET[CGN=@] h:QP[CGN=@]
"""

num_cfg = """
QP ::= h:NUM
"""

adj_cfg = """
AdjP ::= h:ADJ
AdjP ::= AdvMod h:ADJ
AdjP ::= DET[lemma=cel CGN=@] h:AdjP[CGN=@]
AdjP[Number=@ L=@] ::= RP[Number=@ L=care,ce]
AdjP[CGNL=@] ::= VP[CGNL=@ VerbForm==Part]
AdjP[CGN=@ L=@] ::= AdjP[CGNL=@] AdjPConj[CGN=@]
AdjPConj ::= CCONJ h:AdjP[CGN=@] 
"""

noun_cfg = """
N0[det=T Person=3 CGN=@] ::= det:DetP[CGN=@] h:N0[CGN=@ det=F]
N0 ::= h:PRON[PronType!=Rel Strength!=Weak]
N0[Person=3] ::= h:PROPN
N0[Person=3] ::= h:NOUN
N0[Person=3 det=F CGN=@] ::= AdjP[CGN=@] h:N0[CGN=@]
N0 ::= h:N0 id:QP[CGN=@]


NP ::= h:N0
NP[CGN=@] ::= h:NP[CGN=@] AdjP[CGN=@]
NP ::= h:NP poss:NP[Case==Gen]
POSS[PosG=@1 PosN=@2] ::= DET[lemma=al Gender=@1 Number=@2] poss:NP[Case==Gen]
NP ::= h:NP[Gender=@1 Number=@2] POSS[PosG=@1 PosN=@2]
NP ::= h:NP PP
NP ::= h:NP appos:NP[Case=Nom]
"""

adv_cfg = """
AdvMod ::= h:ADV[lemma=prea,foarte,tare,mai]
AdvMod ::= ADV[lemma=mult,și] h:ADV[lemma=mai]
AdvMod ::= DET[lemma=cel] h:ADV[lemma=mai]
AdvMod ::= ADV ADP[lemma=de]    # teribil de 
AdvP ::= h:ADV
AdvP ::= AdvMod h:ADV
AdvP ::= PREP h:AdvP # pe sus, de departe
"""

pp_cfg = """
PREP ::= h:ADP
PREP[Case=@] ::= PREP ADP[Case=@]
PP ::= h:PREP[Case=@] NP[Case=@]
PP ::= h:PREP VP[VerbForm=Inf]    # pentru a scapa
PP ::= h:ADV[lemma=ca,precum] NP
"""

cfg_list = [nom_aliases, det_cfg, num_cfg, adj_cfg, noun_cfg, adv_cfg, pp_cfg]
