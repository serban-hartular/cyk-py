
verb_aliases = """
%%alias VerbForm,Mood,Tense,Person,Number,lemma VMTPNL
%%alias Mood,Tense,Person,Number,lemma MTPNL
%%alias Person,Number,lemma PNL
%%alias Person,Number PN
%%alias Number,lemma NL
"""

verb_cfg = """
V0[VerbForm=Fin MTPNL=@] ::= VERB[VerbForm=Fin MTPNL=@]
V0[VerbForm=Ger MTPNL=@] ::= VERB[VerbForm=Ger MTPNL=@]
V0[VerbForm=Inf MTPNL=@] ::= PART[PartType=Inf] VERB[VerbForm=Inf MTPNL=@]
V0[VerbForm=Part MTPNL=@] ::= VERB[VerbForm=Part MTPNL=@]

AUXP[PNL=@] ::= AUX[PNL=@]
AUXP[PNL=@] ::= AUXP[PNL=@] ADV        # am tot cam mai venit
V0[VerbForm=Fin Mood=Ind Tense=Perf PNL=@] ::= AUXP[lemma=avea PN=@] VERB[VerbForm=Part Gender=Masc Number=Sing lemma=@] 
V0[VerbForm=Fin Mood=Cond Tense=Pres PNL=@] ::= AUXP[lemma=avea PN=@] VERB[VerbForm=Inf lemma=@]
FI_PART[lemma=@] ::= AUX[lemma=fi Tense=Pres VerbForm=Inf] VERB[VerbForm=Part Gender=Masc Number=Sing lemma=@]
V0[VerbForm=Fin Mood=Cond Tense=Perf PNL=@] ::= AUXP[lemma=avea PN=@] FI_PART[lemma=@]
SPART ::= PART[Mood=Sub lemma=să]
SPART ::= SPART ADV # să tot vină
V0[VerbForm=Fin Mood=Sub Tense=Pres Pers=3 NL=@] ::= SPART VERB[VerbForm=Fin Mood=Subj Pers=3 NL=@]
V0[VerbForm=Fin Mood=Sub Tense=Pres Pers=1 NL=@] ::= SPART VERB[VerbForm=Fin Mood=Subj,Ind Pers=1 NL=@]
V0[VerbForm=Fin Mood=Sub Tense=Pres Pers=2 NL=@] ::= SPART VERB[VerbForm=Fin Mood=Subj,Ind Pers=3 NL=@]
V0[VerbForm=Fin Mood=Sub Tense=Perf lemma=@] ::= SPART FI_PART[lemma=@]

"""

vp_cfg = """
%%alias subj,iobj,dobj VARGS
%%alias subj,iobj SI
%%alias subj,dobj SD
%%alias dobj,iobj DI

VP[VMTPNL=@] ::= V0[VMTPNL=@]
VP[MTPNL=@ subj=T DI=@ VerbForm=Fin] ::= subj:NP[Case=Nom Number=@ Person=@] VP[MTPNL=@ subj=F DI=@ VerbForm=Fin]
%reverse
VP[MTPNL=@ dobj=T SI=@ VerbForm=Fin] ::= VP[MTPNL=@ dobj=F SI=@ VerbForm=Fin] dobj:NP[Case=Acc]
%reverse
VP[VMTPNL=@ iobj=T SD=@] ::= VP[VMTPNL=@ iobj=F SD=@] iobj:NP[Case==Dat]
%reverse
VP[VMTPNL=@ VARGS=@] ::= VP[VMTPNL=@ VARGS=@] AdvP
%reverse
VP[VMTPNL=@ VARGS=@] ::= VP[VMTPNL=@ VARGS=@] PP
%reverse

VP[MTPNL=@ dobj=T SI=@ VerbForm=Inf] ::= VP[MTPNL=@ dobj=F SI=@ VerbForm=Inf] dobj:NP[Case=Acc]
%reverse
VP[MTPNL=@ dobj=T SI=@ VerbForm=Ger] ::= VP[MTPNL=@ dobj=F SI=@ VerbForm=Ger] dobj:NP[Case=Acc]
%reverse

"""

cp_cfg = """
SbjvP[Person=@ Number=@ Mood=Sub] ::= PART[Mood==Sub] VP[Person=@ Number=@ Mood=Sub]
CP ::= SCONJ VP
REL ::= PRON[PronType==Rel]
REL ::= ADV[PronType==Rel]
REL ::= PREP[Case=@] REL[Case=@]
RP ::= REL VP
"""

verb_cfg_list = [verb_aliases, verb_cfg, vp_cfg, cp_cfg]


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
AdjP[CNG=@ L=care] ::= RP[CNG=@ L=care,ce]
AdjP[CGNL=@] ::= VP[CGNL=@ VerbForm=Part]
AdjP[CGNL=@] ::= AdvP AdjP[CGNL=@]
AdjP[CGN=@ L=@] ::= AdjP[CGN=@] AdjPConj[CGNL=@]
AdjPConj[CGN=@ L=@] ::= CCONJ[L=@] AdjP[CGN=@] 
"""

noun_cfg = """
N0[CGNPL=@ det=T Person=3] ::= DetP[CGN=@] N0[CGNL=@ det=F]
N0[CGNPL=@] ::= PRON[CGNPL=@ PronType!=Rel]
N0[CGNPL=@] ::= PROPN[CGNPL=@]
N0[CGNL=@ Person=3] ::= NOUN[CGNL=@]
N0[CGNL=@ Person=3] ::= AdjP[CGN=@] NOUN[CGNL=@]
N0[CGNL=@ Person=3] ::= NOUN[CGNL=@] QP


NP[CGNPL=@] ::= N0[CGNPL=@]
NP[CGNPL=@] ::= NP[CGNPL=@] AdjP[CGN=@]
%reverse
NP[CGNPL=@] ::= NP[CGNPL=@] poss:NP[Case==Gen]
%reverse
NP[CGNPL=@] ::= NP[CGNPL=@] PP
NP[CGNPL=@] ::= NP[CGNPL=@] appos:NP[Case=Nom Number=@]
"""

adv_cfg = """
AdvP[L=@] ::= ADV[L=@]
AdvP[L=@] ::= ADP AdvP[L=@] # pe sus, de departe
"""

pp_cfg = """
PREP[Case=@] ::= ADP[Case=@]
PREP[Case=@] ::= PREP ADP[Case=@]
PP ::= PREP[Case=@] NP[Case=@]
PP ::= PREP VP[VerbForm=Inf]    # pentru a scapa
"""

nom_cfg_list = [nom_aliases, det_cfg, num_cfg, adj_cfg, noun_cfg, adv_cfg, pp_cfg]

cfg_list = verb_cfg_list + nom_cfg_list
