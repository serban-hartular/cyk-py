
verb_aliases = """
%%alias VerbForm,Mood,Tense,Person,Number,lemma VMTPNL
%%alias Mood,Tense,Person,Number,lemma MTPNL
%%alias subj,iobj,dobj VARGS
"""

verb_cfg = """
V0[VerbForm=Fin MTPNL=@] ::= VERB[VerbForm=Fin MTPNL=@]
V0[VerbForm=Ger MTPNL=@] ::= VERB[VerbForm=Ger MTPNL=@]
V0[VerbForm=Inf MTPNL=@] ::= PART[PartType=Inf] VERB[VerbForm=Inf MTPNL=@]

"""

vp_cfg = """
VP[VMTPNL=@] ::= V0[VMTPNL=@]
VP[MTPNL=@ subj=T dobj=@ iobj=@ VerbForm=Fin] ::= subj:NP[Case=Nom Number=@ Person=@] VP[VMTPNL=@ subj=F dobj=@ iobj=@ VerbForm=Fin]
%reverse
VP[VMTPNL=@ dobj=T subj=@ iobj=@] ::= VP[VMTPNL=@ dobj=F subj=@ iobj=@] dobj:NP[Case=Acc]
%reverse
VP[VMTPNL=@ iobj=T subj=@ dobj=@] ::= VP[VMTPNL=@ iobj=F subj=@ dobj=@] iobj:NP[Case==Dat]
%reverse
VP[VMTPNL=@ VARGS=@] ::= VP[VMTPNL=@ VARGS=@] AdvP
%reverse
VP[VMTPNL=@ VARGS=@] ::= VP[VMTPNL=@ VARGS=@] PP
%reverse
"""

cp_cfg = """
SbjvP[Person=@ Number=@ Mood=Sub] ::= PART[Mood==Sub] VP[Person=@ Number=@ Mood=Sub]
CP ::= SCONJ VP
REL ::= PRON[PronType=Rel]
REL ::= ADV[PronType=Rel]
REL ::= PREP[Case=@] REL[Case=@]
RP ::= REL VP
"""

cfg_list = [verb_aliases, verb_cfg, vp_cfg, cp_cfg]
