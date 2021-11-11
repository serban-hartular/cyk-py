
verb_aliases = """
%%alias VerbForm,Mood,Tense,Person,Number,lemma VMTPNL
%%alias Mood,Tense,Person,Number,lemma MTPNL
%%alias Person,Number,lemma PNL
%%alias Person,Number PN
%%alias Number,lemma NL
"""


verb_cfg = """
V0 ::= h:VERB[VerbForm=Fin,Ger,Part]
V0 ::= PART[PartType=Inf] h:VERB[VerbForm=Inf]

AUXP ::= h:AUX
AUXP ::= h:AUXP ADV        # am tot cam mai venit
# perfectul compus
V0[VerbForm=Fin Mood=Ind Tense=Perf Comp=T PNL=@] ::= AUXP[lemma=avea PN=@] VERB[VerbForm=Part Gender=Masc Number=Sing lemma=@] 
#conditionalul
V0[VerbForm=Fin Mood=Cond Tense=Pres Comp=T] ::= AUXP[lemma=avea PN=@] h:VERB[VerbForm=Inf]
FI_PART ::= AUX[lemma=fi Tense=Pres VerbForm=Inf] h:VERB[VerbForm=Part Gender=Masc Number=Sing]
V0[VerbForm=Fin Mood=Cond Tense=Perf PN=@ Comp=T] ::= AUXP[lemma=avea PN=@] h:FI_PART
#subjonctivul
SPART ::= h:PART[Mood=Sub lemma=să]
SPART ::= h:SPART ADV # să tot vină
V0[VerbForm=Fin Mood=Subj Tense=Pres] ::= SPART h:V0[VerbForm=Fin Mood=Subj Tense=Pres Pers=3]
V0[VerbForm=Fin Mood=Subj Tense=Pres] ::= SPART h:V0[VerbForm=Fin Mood=Subj,Ind Tense=Pres Pers=1,2]
V0[VerbForm=Fin Mood=Subj Tense=Perf] ::= SPART h:FI_PART[lemma=@]
"""

clitics_cfg = """
DCLT ::= h:PRON[PronType=Prs Strength=Weak Case=Acc]
ICLT ::= h:PRON[PronType=Prs Strength=Weak Case=Dat]
# simple tenses
V0[Dclt=T DcltP=@1 DcltN=@2 DcltG=@3] ::= dclt:DCLT[Person=@1 Number=@2 Gender=@3] h:V0[Dclt=F Iclt=F VerbForm=Fin Comp=F]
V0[Iclt=T IcltP=@1 IcltN=@2 IcltG=@3] ::= iclt:ICLT[Person=@1 Number=@2 Gender=@3] h:V0[Iclt=F VerbForm=Fin Comp=F]
# perfect composite
V0[Dclt=T DcltP=@1 DcltN=@2 DcltG=Masc] ::= dclt:DCLT[Person=@1 Number=@2 Gender=Masc] h:V0[VerbForm=Fin Comp=T Dclt=F Iclt=F]
V0[Dclt=T DcltP=@1 DcltN=@2 DcltG=Fem] ::= h:V0[VerbForm=Fin Comp=T Dclt=F] dclt:DCLT[Person=@1 Number=@2 Gender=Fem]
V0[Iclt=T IcltP=@1 IcltN=@2 IcltG=@3] ::= iclt:ICLT[Person=@1 Number=@2 Gender=@3] h:V0[VerbForm=Fin Comp=T Iclt=F]
"""


vp_cfg = """
%%alias subj,iobj,dobj VARGS

VP ::= h:V0
VP[subj=T] ::= subj:NP[Case=Nom PN=@] h:VP[VerbForm=Fin subj=F PN=@]
%reverse
VP[dobj=T] ::= h:VP[dobj=F VerbForm!=Part DcltP=@1 DcltN=@2 DcltG=@3] dobj:NP[Case=Acc Person=@1 Number=@2 Gender=@3]
%reverse
VP[iobj=T] ::= h:VP[iobj=F IcltP=@1 IcltN=@2 IcltG=@3] iobj:NP[Case==Dat Person=@1 Number=@2 Gender=@3]
%reverse
VP ::= h:VP AdvP
%reverse
VP ::= h:VP PP
%reverse
"""

cp_cfg = """
CP ::= SCONJ VP
REL ::= PRON[PronType==Rel]
REL ::= ADV[PronType==Rel]
REL ::= PREP[Case=@] REL[Case=@]
RP ::= REL VP
"""

cfg_list = [verb_aliases, clitics_cfg, verb_cfg, vp_cfg, cp_cfg]
