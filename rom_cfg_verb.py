
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

cfg_list = [verb_aliases, verb_cfg, vp_cfg, cp_cfg]
