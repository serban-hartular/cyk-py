
verb_aliases = """
%%alias VerbForm,Mood,Tense,Person,Number,lemma VMTPNL
%%alias Mood,Tense,Person,Number,lemma MTPNL
%%alias Person,Number,lemma PNL
%%alias Person,Number PN
%%alias Number,lemma NL
"""


verb_cfg = """
V0 ::= h:VERB[VerbForm=Fin,Ger,Part]
#infinitivul, supinul
V0 ::= PART[PartType=Inf] h:VERB[VerbForm=Inf]
V0[VerbForm=Supin lemma=@] ::= ADP[lemma=de,la,pentru,spre,după] VERB[VerbForm=Part Gender=Masc Number=Sing lemma=@]
#a putea modal
V0[lemma=@1] ::= h:V0[lemma==putea] VERB[VerbForm=Inf lemma=@1] 

AUXP ::= h:AUX
AUXP ::= h:AUXP ADV        # am tot cam mai venit
# perfectul compus
V0[VerbForm=Fin Mood=Ind Tense=Perf Comp=T PNL=@] ::= AUXP[lemma=avea PN=@] VERB[VerbForm=Part Gender=Masc Number=Sing lemma=@] 
#conditionalul
V0[VerbForm=Fin Mood=Cond Tense=Pres Comp=T PN=@] ::= AUXP[lemma=avea PN=@] h:VERB[VerbForm=Inf]
FI_PART[lemma=@] ::= AUX[lemma=fi Tense=Pres VerbForm=Inf] VERB[VerbForm=Part Gender=Masc Number=Sing lemma=@]
V0[VerbForm=Fin Mood=Cond Tense=Perf PN=@ Comp=T lemma=@] ::= AUXP[lemma=avea PN=@] FI_PART[lemma=@]
#subjonctivul
SPART ::= h:PART[Mood=Sub lemma=să]
SPART ::= h:SPART ADV # să tot vină
V0[VerbForm=Fin Mood=Sub Tense=Pres] ::= SPART h:V0[VerbForm=Fin Mood=Sub Tense=Pres Pers=3]
V0[VerbForm=Fin Mood=Sub Tense=Pres] ::= SPART h:V0[VerbForm=Fin Mood=Sub,Ind Tense=Pres Pers=1,2]
V0[VerbForm=Fin Mood=Sub Tense=Perf lemma=@] ::= SPART FI_PART[lemma=@]
"""

clitics_cfg = """
DCLT ::= h:PRON[PronType=Prs Strength=Weak Case=Acc]
ICLT ::= h:PRON[PronType=Prs Strength=Weak Case=Dat]
# simple tenses
V0[Dclt=T DcltP=@1 DcltN=@2 DcltG=@3] ::= dclt:DCLT[Person=@1 Number=@2 Gender=@3] h:V0[Dclt=F Iclt=F VerbForm=Fin Comp=F]
V0[Iclt=T IcltP=@1 IcltN=@2 IcltG=@3] ::= iclt:ICLT[Person=@1 Number=@2 Gender=@3] h:V0[Iclt=F VerbForm=Fin Comp=F]
# perfect composite
V0[Dclt=T DcltP=@1 DcltN=@2 DcltG=Masc] ::= dclt:DCLT[Person=@1 Number=@2 Gender=Masc] h:V0[VerbForm=Fin Comp==T Dclt=F Iclt=F]
V0[Dclt=T DcltP=@1 DcltN=@2 DcltG=Fem] ::= h:V0[VerbForm=Fin Comp==T Dclt=F] dclt:DCLT[Person=@1 Number=@2 Gender=Fem]
V0[Iclt=T IcltP=@1 IcltN=@2 IcltG=@3] ::= iclt:ICLT[Person=@1 Number=@2 Gender=@3] h:V0[VerbForm=Fin Comp==T Iclt=F]
"""


vp_cfg = """
PE_DOBJ ::= ADP[lemma=pe] h:NP[Case=Acc]

VP ::= h:V0
VP[neg=T] ::= PART[Polarity==Neg] h:V0
# subject
VP[subj=T SubjG=@1] ::= subj:NP[Case=Nom PN=@ Gender=@1] h:VP[VerbForm=Fin subj=F PN=@]
%reverse
# direct object
VP[dobj=T] ::= h:VP[dobj=F VerbForm!=Part DcltP=@1 DcltN=@2 DcltG=@3] dobj:NP[Case=Acc Person=@1 Number=@2 Gender=@3]
%reverse
VP[dobj=T] ::= h:VP[dobj=F Dclt==T VerbForm!=Part DcltP=@1 DcltN=@2 DcltG=@3] dobj:PE_DOBJ[Person=@1 Number=@2 Gender=@3]
%reverse
VP[dobj=T] ::= h:VP[dobj=F] dobj:VP[Mood==Sub]
# indirect object
VP[iobj=T] ::= h:VP[iobj=F IcltP=@1 IcltN=@2 IcltG=@3] iobj:NP[Case==Dat Person=@1 Number=@2 Gender=@3]
%reverse
# copulative predicate
VP[cop=T] ::= h:VP[cop=F dobj=F SubjG=@1 Number=@ lemma=fi] npred:NP[Case=Nom Gender=@1 Number=@]  
VP[cop=T] ::= h:VP[cop=F dobj=F SubjG=@1 Number=@ lemma=fi] npred:AdjP[Case=Nom Gender=@1 Number=@]  

# adverbs, prepositional phrases
VP ::= h:VP AdvP
%reverse
VP ::= h:VP PP
%reverse
"""

cp_cfg = """
SConj ::= SCONJ
SConj ::= ADP[lemma=pentru] ADV[lemma=ca]
CP ::= SConj VP[VerbForm=Fin]
REL ::= PRON[PronType==Rel]
REL ::= ADV[PronType==Rel]
REL ::= PREP[Case=@] REL[Case=@]
RP ::= REL VP
"""

sub_clause = """
VP ::= h:VP CP
%reverse
VP ::= h:VP RP
%reverse
"""

cfg_list = [verb_aliases, clitics_cfg, verb_cfg, vp_cfg, cp_cfg, sub_clause]
