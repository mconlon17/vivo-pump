#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    improve -- module of functions for improving (standard spacing, punctuation, resoltuion of abbreviations,
    conformance to international standards) text string data
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright (c) 2016 Michael Conlon"
__license__ = "New BSD license"
__version__ = "0.1"


class FilterNotFoundException(Exception):
    """
    Raise this exception when a filter can not be found
    """
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidDataException(Exception):
    """
    Raise this exception when update data contains values that can not be processed
    """
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)


def comma_space(s):
    """
    insert a space after every comma in s unless s ends in a comma
    :param s: string to be checked for spaces after commas
    :return s: improved string with commas always followed by spaces
    :rtype: basestring
    """
    k = s.find(',')
    if -1 < k < len(s) - 1 and s[k + 1] != " ":
        s = s[0:k] + ', ' + comma_space(s[k + 1:])
    return s


def improve_email(email):
    """
    Given an email string, fix it
    """
    import re
    exp = re.compile(r'\w+\.*\w+@\w+\.(\w+\.*)*\w+')
    s = exp.search(email.lower())
    if s is None:
        return ""
    elif s.group() is not None:
        return s.group()
    else:
        return ""


def improve_phone_number(phone):
    """
    Given an arbitrary string that attempts to represent a phone number,
    return a best attempt to format the phone number according to ITU standards

    If the phone number can not be repaired, the function returns an empty string
    """
    phone_text = phone.encode('ascii', 'ignore')  # encode to ascii
    phone_text = phone_text.lower()
    phone_text = phone_text.strip()
    extension_digits = None
    #
    # strip off US international country code
    #
    if phone_text.find('+1 ') == 0:
        phone_text = phone_text[3:]
    if phone_text.find('+1-') == 0:
        phone_text = phone_text[3:]
    if phone_text.find('(1)') == 0:
        phone_text = phone_text[3:]
    digits = []
    for c in list(phone_text):
        if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            digits.append(c)
    if len(digits) > 10 or phone_text.rfind('x') > -1:
        # pull off the extension
        i = phone_text.rfind(' ')  # last blank
        if i > 0:
            extension = phone_text[i + 1:]
            extension_digits = []
            for c in list(extension):
                if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    extension_digits.append(c)
            digits = []  # reset the digits
            for c in list(phone_text[:i + 1]):
                if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    digits.append(c)
        elif phone_text.rfind('x') > 0:
            i = phone_text.rfind('x')
            extension = phone_text[i + 1:]
            extension_digits = []
            for c in list(extension):
                if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    extension_digits.append(c)
            digits = []  # recalculate the digits
            for c in list(phone_text[:i + 1]):
                if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    digits.append(c)
        else:
            extension_digits = digits[10:]
            digits = digits[:10]
    if len(digits) == 7:
        if phone[0:5] == '352392':
            updated_phone = ''  # Damaged UF phone number, nothing to repair
            extension_digits = None
        elif phone[0:5] == '352273':
            updated_phone = ''  # Another damaged phone number, not to repair
            extension_digits = None
        else:
            updated_phone = '(352) ' + "".join(digits[0:3]) + '-' + "".join(digits[3:7])
    elif len(digits) == 10:
        updated_phone = '(' + "".join(digits[0:3]) + ') ' + "".join(digits[3:6]) + \
                        '-' + "".join(digits[6:10])
    elif len(digits) == 5 and digits[0] == '2':  # UF special
        updated_phone = '(352) 392-' + "".join(digits[1:5])
    elif len(digits) == 5 and digits[0] == '3':  # another UF special
        updated_phone = '(352) 273-' + "".join(digits[1:5])
    else:
        updated_phone = ''  # no repair
        extension_digits = None
    if extension_digits is not None and len(extension_digits) > 0:
        updated_phone = updated_phone + ' ext. ' + "".join(extension_digits)
    return updated_phone


def improve_course_title(s):
    """
    The Office of the University Registrar at UF uses a series of abbreviations to fit course titles into limited text
    strings.
    Here we attempt to reverse the process -- a short title is turned into a
    longer one for use in labels
    """
    abbrev_table = {
        "Intro ": "Introduction ",
        "To ": "to ",
        "Of ": "of ",
        "In ": "in ",
        "Stat ": "Statistics ",
        "Spec ": "Special ",
        "Top ": "Topics ",
        "Hist ": "History ",
        "Hlthcare ": "Healthcare ",
        "Prac ": "Practice "
    }
    s = s.lower()  # convert to lower
    s = s.title()  # uppercase each word
    s += ' '       # add a trailing space so we can find these abbreviated words throughout the string
    t = unicode(s.replace(", ,", ","))
    t = t.replace("  ", " ")
    t = t.replace("/", " @")
    t = t.replace("/", " @")  # might be two slashes in the input
    t = t.replace(",", " !")
    t = t.replace("-", " #")
    for abbrev in abbrev_table:
        t = t.replace(abbrev, abbrev_table[abbrev])
    t = t.replace(" @", "/")  # restore /
    t = t.replace(" @", "/")  # restore /
    t = t.replace(" !", ",")  # restore ,
    t = t.replace(" !", ",")  # restore ,
    t = t.replace(" #", "-")  # restore -
    t = comma_space(t.strip())
    return t[0].upper() + t[1:]


def improve_jobcode_description(s):
    """
    HR uses a series of abbreviations to fit job titles into limited text
    strings.
    Here we attempt to reverse the process -- a short title is turned into a
    longer one for use in position labels
    """
    abbrev_table = {
        "Aca ": "Academic ",
        "Act ": "Acting ",
        "Adj ": "Adjunct ",
        "Adm ": "Administrator ",
        "Admin ": "Administrative ",
        "Adv ": "Advisory ",
        "Advanc ": "Advanced ",
        "Aff ": "Affiliate ",
        "Affl ": "Affiliate ",
        "Agric ": "Agricultural ",
        "Alumn Aff ": "Alumni Affairs ",
        "Anal  ": "Analyst ",
        "Anlst ": "Analyst ",
        "Aso ": "Associate ",
        "Asoc ": "Associate ",
        "Assoc ": "Associate ",
        "Asst ": "Assistant ",
        "Asst. ": "Assistant ",
        "Ast ": "Assistant ",
        "Ast #G ": "Grading Assistant ",
        "Ast #R ": "Research Assistant ",
        "Ast #T ": "Teaching Assistant ",
        "Bio ": "Biological ",
        "Cfo ": "Chief Financial Officer ",
        "Chem ": "Chemist ",
        "Chr ": "Chair ",
        "Cio ": "Chief Information Officer ",
        "Clin ": "Clinical ",
        "Clrk ": "Clerk ",
        "Co ": "Courtesy ",
        "Comm ": "Communications ",
        "Communic ": "Communications ",
        "Coo ": "Chief Operating Officer ",
        "Coord ": "Coordinator ",
        "Couns ": "Counselor ",
        "Crd ": "Coordinator ",
        "Ctr ": "Center ",
        "Ctsy ": "Courtesy ",
        "Cty ": "County ",
        "Dev ": "Development ",
        "Devel ": "Development ",
        "Dir ": "Director ",
        "Dis ": "Distinguished ",
        "Dist ": "Distinguished ",
        "Div ": "Division ",
        "Dn ": "Dean ",
        "Educ ": "Education ",
        "Emer ": "Emeritus ",
        "Emin ": "Eminent ",
        "Enforce ": "Enforcement ",
        "Eng ": "Engineer ",
        "Environ ": "Environmental ",
        "Ext ": "Extension ",
        "Facil ": "Facility ",
        "Fin ": "Financial",
        "Finan ": "Financial ",
        "Gen ": "General ",
        "Grd ": "Graduate ",
        "Hlt ": "Health ",
        "Hlth ": "Health ",
        "Ii ": "II ",
        "Iii ": "III ",
        "Info ": "Information ",
        "Int ": "Interim ",
        "It ": "Information Technology ",
        "Iv ": "IV ",
        "Jnt ": "Joint ",
        "Jr": "Junior",
        "Lect ": "Lecturer ",
        "Mgr ": "Manager ",
        "Mgt ": "Management ",
        "Mstr ": "Master ",
        "Opr ": "Operator ",
        "Phas ": "Phased ",
        "Pky ": "PK Yonge ",
        "Postdoc ": "Postdoctoral ",
        "Pract ": "Practitioner ",
        "Pres ": "President ",
        "Pres5 ": "President 5 ",
        "Pres6 ": "President 6 ",
        "Prg ": "Program ",
        "Prof ": "Professor ",
        "Prof. ": "Professor ",
        "Prog ": "Programmer ",
        "Progs ": "Programs ",
        "Prov ": "Provisional ",
        "Radiol ": "Radiology ",
        "Rcv ": "Receiving ",
        "Registr ": "Registration ",
        "Rep ": "Representative ",
        "Res ": "Research ",
        "Ret ": "Retirement ",
        "Rsch ": "Research ",
        "Rsrh ": "Research ",
        "Sch ": "School ",
        "Sci ": "Scientist ",
        "Sctst ": "Scientist ",
        "Ser ": "Service ",
        "Serv ": "Service ",
        "Spc ": "Specialist ",
        "Spec ": "Specialist ",
        "Spv ": "Supervisor ",
        "Sr ": "Senior ",
        "Stu ": "Student ",
        "Stud ": "Student",
        "Supp ": "Support ",
        "Supt ": "Superintendent ",
        "Supv ": "Supervisor ",
        "Svcs ": "Services ",
        "Tch ": "Teaching ",
        "Tech ": "Technician ",
        "Technol ": "Technologist ",
        "Tele ": "Telecommunications ",
        "Tv ": "TV ",
        "Univ ": "University ",
        "Vis ": "Visiting ",
        "Vp ": "Vice President "
    }
    s = s.lower()  # convert to lower
    s = s.title()  # uppercase each word
    s += ' '       # add a trailing space so we can find these abbreviated words throughout the string
    t = unicode(s.replace(", ,", ","))
    t = t.replace("&", " and ")
    t = t.replace("  ", " ")
    t = t.replace("/", " @")
    t = t.replace("/", " @")  # might be two slashes in the input
    t = t.replace(",", " !")

    for abbrev in abbrev_table:
        t = t.replace(abbrev, abbrev_table[abbrev])
    t = t.replace(" @", "/")  # restore /
    t = t.replace(" @", "/")
    t = t.replace(" !", ",")  # restore ,
    t = t.replace(" #", "-")  # restore -
    return t[:-1]  # Take off the trailing space


def improve_org_name(s):
    """
    Organization names are often abbreviated and sometime misspelled. Build a translation table here of
    corrections/improvements to org names
    :param s:
    :return:
    :rtype: string
    """
    abbrev_table = {
        " & ": " and ",
        "'S ": "'s ",
        " A ": " a ",
        "Aav ": "AAV ",
        "Aca ": "Academy ",
        "Acad ": "Academy ",
        "Admn ": "Administration ",
        "Adv ": "Advanced ",
        "Advanc ": "Advanced ",
        "Ag ": "Agriculture ",
        "Agri ": "Agriculture ",
        "Amer ": "American ",
        "And ": "and ",
        "Analysists ": "Analysts ",
        "Asso ": "Association ",
        "Assoc ": "Association ",
        "At ": "at ",
        "Bldg ": "Building ",
        "Bpm ": "BPM ",
        "Brcc ": "BRCC ",
        "Childrens ": "Children's ",
        "Clin ": "Clinical ",
        "Clncl ": "Clinical ",
        "Cms ": "CMS ",
        "Cns ": "CNS ",
        "Cncl ": "Council ",
        "Cncr ": "Cancer ",
        "Cnty ": "County ",
        "Co ": "Company ",
        "Cog ": "COG ",
        "Col ": "College ",
        "Coll ": "College ",
        "Communic ": "Communications ",
        "Compar ": "Compare ",
        "Coo ": "Chief Operating Officer ",
        "Corp ": "Corporation ",
        "Cpb ": "CPB ",
        "Crd ": "Coordinator ",
        "Cse ": "CSE ",
        "Ctr ": "Center ",
        "Cty ": "County ",
        "Cwp ": "CWP ",
        "Dbs ": "DBS ",
        "Dept ": "Department ",
        "Dev ": "Development ",
        "Devel ": "Development ",
        "Dist ": "Distinguished ",
        "Dna ": "DNA ",
        "Doh ": "DOH ",
        "Doh/cms ": "DOH/CMS ",
        "Double Blinded ": "Double-blind ",
        "Double-blinded ": "Double-blind ",
        "Dpt-1 ": "DPT-1 ",
        "Dtra0001 ": "DTRA0001 ",
        "Dtra0016 ": "DTRA-0016 ",
        "Edu ": "Education ",
        "Educ ": "Education ",
        "Eff/saf ": "Safety and Efficacy ",
        "Eh&S ": "EH&S ",
        "Emer ": "Emeritus ",
        "Emin ": "Eminent ",
        "Enforce ": "Enforcement ",
        "Eng ": "Engineer ",
        "Environ ": "Environmental ",
        "Epr ": "EPR ",
        "Eval ": "Evaluation ",
        "Ext ": "Extension ",
        "Fdot ": "FDOT ",
        "Fdots ": "FDOT ",
        "Fhtcc ": "FHTCC ",
        "Finan ": "Financial ",
        "Fl ": "Florida ",
        "Fla ": "Florida ",
        "Fllw ": "Follow ",
        "Fndt ": "Foundation ",
        "For ": "for ",
        "Fou ": "Foundation ",
        "G-csf ": "G-CSF ",
        "Gen ": "General ",
        "Gis ": "GIS ",
        "Gm-csf ": "GM-CSF ",
        "Grad ": "Graduate ",
        "Hcv ": "HCV ",
        "Hiv ": "HIV ",
        "Hiv-infected ": "HIV-infected ",
        "Hiv/aids ": "HIV/AIDS ",
        "Hlb ": "HLB ",
        "Hlth ": "Health ",
        "Hosp ": "Hospital ",
        "Hou ": "Housing ",
        "Hsv-1 ": "HSV-1 ",
        "I/ii ": "I/II ",
        "I/ucrc ": "I/UCRC ",
        "Ica ": "ICA ",
        "Icd ": "ICD ",
        "Ieee ": "IEEE ",
        "Ifas ": "IFAS ",
        "Igf-1 ": "IGF-1 ",
        "Ii ": "II ",
        "Ii/iii ": "II/III ",
        "Iii ": "III ",
        "In ": "in ",
        "Info ": "Information ",
        "Inst ": "Institute ",
        "Intl ": "International ",
        "Intervent ": "Intervention ",
        "Ipa ": "IPA ",
        "Ipm ": "IPM ",
        "Ippd ": "IPPD ",
        "Ips ": "IPS ",
        "It ": "Information Technology ",
        "Iv ": "IV ",
        "Jnt ": "Joint ",
        "Lng ": "Long ",
        "Mccarty ": "McCarty ",
        "Mgmt ": "Management ",
        "Mgr ": "Manager ",
        "Mgt ": "Management ",
        "Mlti ": "Multi ",
        "Mlti-ctr ": "Multicenter ",
        "Mltictr ": "Multicenter ",
        "Mri ": "MRI ",
        "Mstr ": "Master ",
        "Multi-center ": "Multicenter ",
        "Multi-ctr ": "Multicenter ",
        "Natl ": "National ",
        "Nih ": "NIH ",
        "Nmr ": "NMR ",
        "Nsf ": "NSF ",
        "Ne ": "NE ",
        "Nw ": "NW ",
        "Of ": "of ",
        "On ": "on ",
        "Or ": "or ",
        "Open-labeled ": "Open-label ",
        "Opn-lbl ": "Open-label ",
        "Opr ": "Operator ",
        "Org ": "Organization ",
        "Pgm ": "Program ",
        "Phas ": "Phased ",
        "Php ": "PHP ",
        "Phs ": "PHS ",
        "Pk/pd ": "PK/PD ",
        "Pky ": "P. K. Yonge ",
        "Plcb-ctrl ": "Placebo-controlled ",
        "Plcbo ": "Placebo ",
        "Plcbo-ctrl ": "Placebo-controlled ",
        "Postdoc ": "Postdoctoral ",
        "Pract ": "Practitioner ",
        "Pres5 ": "President 5 ",
        "Pres6 ": "President 6 ",
        "Prg ": "Programs ",
        "Prof ": "Professor ",
        "Prog ": "Programmer ",
        "Progs ": "Programs ",
        "Prov ": "Provisional ",
        "Psr ": "PSR ",
        "Radiol ": "Radiology ",
        "Rcv ": "Receiving ",
        "Rdmzd ": "Randomized ",
        "Heat Refrig Air Con": "Heating, Refrigerating and Air-Conditioning Engineers",
        "Rep ": "Representative ",
        "Res ": "Research ",
        "Ret ": "Retirement ",
        "Reu ": "REU ",
        "Rna ": "RNA ",
        "Rndmzd ": "Randomized ",
        "Rsch ": "Research ",
        "Saf ": "SAF ",
        "Saf/eff ": "Safety and Efficacy ",
        "Sbjcts ": "Subjects ",
        "Sch ": "School ",
        "Se ": "SE ",
        "Ser ": "Service ",
        "Sfwmd ": "SFWMD ",
        "Sle ": "SLE ",
        "Sntc ": "SNTC ",
        "Soc ": "Society ",
        "Spec ": "Specialist ",
        "Spnsrd ": "Sponsored ",
        "Spv ": "Supervisor ",
        "Sr ": "Senior ",
        "Stdy ": "Study ",
        "Stratagies ": "Strategies ",
        "Subj ": "Subject ",
        "Supp ": "Support ",
        "Supt ": "Superintendant ",
        "Supv ": "Supervisor ",
        "Svc ": "Services ",
        "Svcs ": "Services ",
        "Sw ": "SW ",
        "Tch ": "Teaching ",
        "Tech ": "Technician ",
        "Technol ": "Technologist ",
        "Teh ": "the ",
        "The ": "the ",
        "To ": "to ",
        "Trls ": "Trials ",
        "Trm ": "Term ",
        "Tv ": "TV ",
        "Uaa ": "UAA ",
        "Uf ": "UF ",
        "Ufrf ": "UFRF ",
        "Uhf ": "UHF ",
        "Univ ": "University ",
        "Usa ": "USA ",
        "Us ": "US ",
        "Va ": "VA ",
        "Vhf ": "VHF ",
        "Vis ": "Visiting ",
        "Vp ": "Vice President ",
        "Wuft-Fm ": "WUFT-FM "
    }
    if s == "":
        return s
    if s[len(s) - 1] == ',':
        s = s[0:len(s) - 1]
    if s[len(s) - 1] == ',':
        s = s[0:len(s) - 1]
    s = s.lower()  # convert to lower
    s = s.title()  # uppercase each word
    s += ' '    # add a trailing space so we can find these abbreviated words throughout the string
    t = unicode(s.replace(", ,", ","))
    t = t.replace("  ", " ")
    t = t.replace("/", " @")
    t = t.replace("/", " @")  # might be two slashes in the input
    t = t.replace(",", " !")
    t = t.replace(",", " !")  # might be two commas in input

    for abbrev in abbrev_table:
        t = t.replace(abbrev, abbrev_table[abbrev])

    t = t.replace(" @", "/")  # restore /
    t = t.replace(" @", "/")
    t = t.replace(" !", ",")  # restore ,
    t = t.replace(" !", ",")  # restore ,
    t = comma_space(t.strip())
    return t[0].upper() + t[1:]


def improve_title(s):
    """
    DSP, HR, funding agencies and others use a series of abbreviations to fit grant titles into limited text
    strings.  Systems often restrict the length of titles of various kinds and people often clip their titles to
    fit in available space.  Here we reverse the process and lengthen the name for readability
    :param s:
    :return:
    :rtype: basestring
    """
    abbrev_table = {
        "'S ": "'s ",
        "2-blnd ": "Double-blind ",
        "2blnd ": "Double-blind ",
        "A ": "a ",
        "Aav ": "AAV ",
        "Aca ": "Academic ",
        "Acad ": "Academic ",
        "Acp ": "ACP ",
        "Acs ": "ACS ",
        "Act ": "Acting ",
        "Adj ": "Adjunct ",
        "Adm ": "Administrator ",
        "Admin ": "Administrative ",
        "Adv ": "Advisory ",
        "Advanc ": "Advanced ",
        "Aff ": "Affiliate ",
        "Affl ": "Affiliate ",
        "Ahec ": "AHEC ",
        "Aldh ": "ALDH ",
        "Alk1 ": "ALK1 ",
        "Alumn Aff ": "Alumni Affairs ",
        "Amd3100 ": "AMD3100 ",
        "And ": "and ",
        "Aso ": "Associate ",
        "Asoc ": "Associate ",
        "Assoc ": "Associate ",
        "Ast ": "Assistant ",
        "Ast #G ": "Grading Assistant ",
        "Ast #R ": "Research Assistant ",
        "Ast #T ": "Teaching Assistant ",
        "At ": "at ",
        "Bldg ": "Building ",
        "Bpm ": "BPM ",
        "Brcc ": "BRCC ",
        "Cfo ": "Chief Financial Officer ",
        "Cio ": "Chief Information Officer ",
        "Clin ": "Clinical ",
        "Clncl ": "Clinical ",
        "Cms ": "CMS ",
        "Cns ": "CNS ",
        "Cncr ": "Cancer ",
        "Co ": "Courtesy ",
        "Cog ": "COG ",
        "Communic ": "Communications ",
        "Compar ": "Compare ",
        "Coo ": "Chief Operating Officer ",
        "Copd ": "COPD ",
        "Cpb ": "CPB ",
        "Crd ": "Coordinator ",
        "Cse ": "CSE ",
        "Ctr ": "Center ",
        "Cty ": "County ",
        "Cwp ": "CWP ",
        "Dbl-bl ": "Double-blind ",
        "Dbl-blnd ": "Double-blind ",
        "Dbs ": "DBS ",
        "Dev ": "Development ",
        "Devel ": "Development ",
        "Dist ": "Distinguished ",
        "Dna ": "DNA ",
        "Doh ": "DOH ",
        "Doh/cms ": "DOH/CMS ",
        "Double Blinded ": "Double-blind ",
        "Double-blinded ": "Double-blind ",
        "Dpt-1 ": "DPT-1 ",
        "Dtra0001 ": "DTRA0001 ",
        "Dtra0016 ": "DTRA-0016 ",
        "Educ ": "Education ",
        "Eff/saf ": "Safety and Efficacy ",
        "Eh&S ": "EH&S ",
        "Emer ": "Emeritus ",
        "Emin ": "Eminent ",
        "Enforce ": "Enforcement ",
        "Eng ": "Engineer ",
        "Environ ": "Environmental ",
        "Epr ": "EPR ",
        "Eval ": "Evaluation ",
        "Ext ": "Extension ",
        "Fdot ": "FDOT ",
        "Fdots ": "FDOT ",
        "Fhtcc ": "FHTCC ",
        "Finan ": "Financial ",
        "Fla ": "Florida ",
        "Fllw ": "Follow ",
        "For ": "for ",
        "G-csf ": "G-CSF ",
        "Gen ": "General ",
        "Gis ": "GIS ",
        "Gm-csf ": "GM-CSF ",
        "Grad ": "Graduate ",
        "Hcv ": "HCV ",
        "Hiv ": "HIV ",
        "Hiv-infected ": "HIV-infected ",
        "Hiv/aids ": "HIV/AIDS ",
        "Hlb ": "HLB ",
        "Hlth ": "Health ",
        "Hou ": "Housing ",
        "Hsv-1 ": "HSV-1 ",
        "I/ii ": "I/II ",
        "I/ucrc ": "I/UCRC ",
        "Ica ": "ICA ",
        "Icd ": "ICD ",
        "Ieee ": "IEEE ",
        "Ifas ": "IFAS ",
        "Igf-1 ": "IGF-1 ",
        "Ii ": "II ",
        "Ii/iii ": "II/III ",
        "Iii ": "III ",
        "In ": "in ",
        "Info ": "Information ",
        "Inter-vention ": "Intervention ",
        "Ipa ": "IPA ",
        "Ipm ": "IPM ",
        "Ippd ": "IPPD ",
        "Ips ": "IPS ",
        "It ": "Information Technology ",
        "Iv ": "IV ",
        "Jnt ": "Joint ",
        "Lng ": "Long ",
        "Mccarty ": "McCarty ",
        "Mgmt ": "Management ",
        "Mgr ": "Manager ",
        "Mgt ": "Management ",
        "Mlti ": "Multi ",
        "Mlti-ctr ": "Multicenter ",
        "Mltictr ": "Multicenter ",
        "Mri ": "MRI ",
        "Mstr ": "Master ",
        "Multi-center ": "Multicenter ",
        "Multi-ctr ": "Multicenter ",
        "Nih ": "NIH ",
        "Nmr ": "NMR ",
        "Nsf ": "NSF ",
        "Ne ": "NE ",
        "Nw ": "NW ",
        "Of ": "of ",
        "On ": "on ",
        "Or ": "or ",
        "Open-labeled ": "Open-label ",
        "Opn-lbl ": "Open-label ",
        "Opr ": "Operator ",
        "Phas ": "Phased ",
        "Php ": "PHP ",
        "Phs ": "PHS ",
        "Pk/pd ": "PK/PD ",
        "Pky ": "P. K. Yonge ",
        "Plcb-ctrl ": "Placebo-controlled ",
        "Plcbo ": "Placebo ",
        "Plcbo-ctrl ": "Placebo-controlled ",
        "Postdoc ": "Postdoctoral ",
        "Pract ": "Practitioner ",
        "Pres5 ": "President 5 ",
        "Pres6 ": "President 6 ",
        "Prg ": "Programs ",
        "Prof ": "Professor ",
        "Prog ": "Programmer ",
        "Progs ": "Programs ",
        "Prov ": "Provisional ",
        "Psr ": "PSR ",
        "Radiol ": "Radiology ",
        "Rcv ": "Receiving ",
        "Rdmzd ": "Randomized ",
        "Rep ": "Representative ",
        "Res ": "Research ",
        "Ret ": "Retirement ",
        "Reu ": "REU ",
        "Rna ": "RNA ",
        "Rndmzd ": "Randomized ",
        "Roc-124 ": "ROC-124 ",
        "Rsch ": "Research ",
        "Saf ": "SAF ",
        "Saf/eff ": "Safety and Efficacy ",
        "Sbjcts ": "Subjects ",
        "Sch ": "School ",
        "Se ": "SE ",
        "Ser ": "Service ",
        "Sfwmd ": "SFWMD ",
        "Sle ": "SLE ",
        "Sntc ": "SNTC ",
        "Spec ": "Specialist ",
        "Spnsrd ": "Sponsored ",
        "Spv ": "Supervisor ",
        "Sr ": "Senior ",
        "Stdy ": "Study ",
        "Subj ": "Subject ",
        "Supp ": "Support ",
        "Supt ": "Superintendant ",
        "Supv ": "Supervisor ",
        "Svc ": "Services ",
        "Svcs ": "Services ",
        "Sw ": "SW ",
        "Tch ": "Teaching ",
        "Tech ": "Technician ",
        "Technol ": "Technologist ",
        "Teh ": "the ",
        "The ": "the ",
        "To ": "to ",
        "Trls ": "Trials ",
        "Trm ": "Term ",
        "Tv ": "TV ",
        "Uaa ": "UAA ",
        "Uf ": "UF ",
        "Ufrf ": "UFRF ",
        "Uhf ": "UHF ",
        "Univ ": "University ",
        "Us ": "US ",
        "Usa ": "USA ",
        "Va ": "VA ",
        "Vhf ": "VHF ",
        "Vis ": "Visiting ",
        "Vp ": "Vice President ",
        "Wuft-Fm ": "WUFT-FM "
    }
    if s == "":
        return s
    if s[len(s) - 1] == ',':
        s = s[0:len(s) - 1]
    if s[len(s) - 1] == ',':
        s = s[0:len(s) - 1]
    s = s.lower()  # convert to lower
    s = s.title()  # uppercase each word
    s += ' '    # add a trailing space so we can find these abbreviated words throughout the string
    t = s.replace(", ,", ",")
    t = t.replace("  ", " ")
    t = t.replace("/", " @")
    t = t.replace("/", " @")  # might be two slashes in the input
    t = t.replace(",", " !")
    t = t.replace(",", " !")  # might be two commas in input

    for abbrev in abbrev_table:
        t = t.replace(abbrev, abbrev_table[abbrev])

    t = t.replace(" @", "/")  # restore /
    t = t.replace(" @", "/")
    t = t.replace(" !", ",")  # restore ,
    t = t.replace(" !", ",")  # restore ,
    t = comma_space(t.strip())
    return t[0].upper() + t[1:]


def improve_dollar_amount(s):
    """
    given a text string s that should be a dollar amount, return a string that looks like n*.nn
    :param s: the string to be improved
    :return: the improved string
    """
    import re
    pattern = re.compile('[0-9]*[0-9]\.[0-9][0-9]')
    s = s.replace(' ', '')
    s = s.replace('$', '')
    s = s.replace(',', '')
    if '.' not in s:
        s += '.00'
    if s[0] == '.':
        s = '0' + s
    m = pattern.match(s)
    if not m:
        raise InvalidDataException(s + ' not a valid dollar amount')
    return s


def improve_date(s):
    """
    Given a string representing a date, year month day, return a string that is standard UTC format.
    :param s: the string to be improved.  Several input date formats are supported including slashes, spaces or dashes
    for separators, variable digits for year, month and day.
    :return: improved date string
    :rtype: string
    """
    import re
    from datetime import date

    month_words = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11,
        'dec': 12, 'january': 1, 'february': 2, 'march': 3, 'april': 4, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    all_numbers = re.compile('([0-9]+)[-/, ]([0-9]+)[-/, ]([0-9]+)')
    middle_word = re.compile('([0-9]+)[-/, ]([a-zA-Z]+)[-,/ ]([0-9]+)')
    match_object = all_numbers.match(s)
    if match_object:
        y = int(match_object.group(1))
        m = int(match_object.group(2))
        d = int(match_object.group(3))
    else:
        match_object = middle_word.match(s)
        if match_object:
            y = int(match_object.group(1))
            m = month_words.get(match_object.group(2).lower(), None)
            if m is None:
                raise InvalidDataException(s + ' is not a valid date')
            d = int(match_object.group(3))
        else:
            raise InvalidDataException(s + ' did not match a date pattern')
    if y < 100:
        y += 2000
    date_value = date(y, m, d)
    date_string = date_value.isoformat()
    return date_string


def improve_deptid(s):
    """
    Given a string with a deptid, confirm validity, add leading zeros if needed
    :param s: string deptid
    :return: string improved deptid
    :rtype: string
    """
    import re
    deptid_pattern = re.compile('([0-9]{1,8})')
    match_object = deptid_pattern.match(s)
    if match_object:
        return match_object.group(1).rjust(8, '0')
    else:
        raise InvalidDataException(s + ' is not a valid deptid')


def improve_display_name(s):
    """
    Give a display name s, fix it up into a standard format -- last name, comma, first name (or initial), middle name
    or initials.  Initials are followed with a period and a space.  No trailing space at the end of the display_name
    :param s: Display names in a variety of formats
    :return: standard display name
    """
    s = s.title()  # Capitalize each word
    s = comma_space(s)  # put a blank after the comma
    s = s.strip()  # remove trailing spaces
    return s


def improve_sponsor_award_id(s):
    """
    Given a string with a sponsor award id, standardize presentation and regularize NIH award ids
    :param s: string with sponsor award id
    :return: string improved sponsor award id
    :rtype: string
    """
    import re
    s = s.strip()
    nih_pattern = re.compile('.*([A-Za-z][0-9][0-9]).*([A-Za-z][A-Za-z][0-9]{6})')
    match_object = nih_pattern.match(s)
    if match_object:
        return match_object.group(1).upper() + match_object.group(2).upper()
    else:
        return s


def improve(improve_name, improve_text):
    """
    Given the name of an improve function and the text to be improved, call the function on the text and
    return the result.

    This function is provided in lieu of using an eval
    :param improve_name: name of improve function
    :param improve_text: text to be improved
    :return:  improved text
    """
    if improve_name == 'improve_email':
        return improve_email(improve_text)
    elif improve_name == 'improve_phone_number':
        return improve_phone_number(improve_text)
    elif improve_name == 'improve_course_title':
        return improve_course_title(improve_text)
    elif improve_name == 'improve_jobcode_description':
        return improve_jobcode_description(improve_text)
    elif improve_name == 'improve_org_name':
        return improve_org_name(improve_text)
    elif improve_name == 'improve_title':
        return improve_title(improve_text)
    elif improve_name == 'improve_dollar_amount':
        return improve_dollar_amount(improve_text)
    elif improve_name == 'improve_date':
        return improve_date(improve_text)
    elif improve_name == 'improve_deptid':
        return improve_deptid(improve_text)
    elif improve_name == 'improve_display_name':
        return improve_display_name(improve_text)
    elif improve_name == 'improve_sponsor_award_id':
        return improve_sponsor_award_id(improve_text)
    else:
        raise FilterNotFoundException(improve_name)
