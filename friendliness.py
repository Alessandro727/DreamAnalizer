import spacy
import json
import nltk
import re
from nltk import pos_tag
from nltk import tokenize
from nltk.tree import Tree
#from nltk.parse.stanford import StanfordParser
from nltk.stem.wordnet import WordNetLemmatizer
from characters import *
from emotions import *
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


"""
Script created for the extraction and encoding of sexuality interactions between characters within dream reports. 
To understand the rules of sexuality interactions identification visit the following link: 
https://dreams.ucsc.edu/Coding/friendliness.html
"""



analyser = SentimentIntensityAnalyzer()

##########################
# Find the sentiment score of a sentence.
# Parameter:
# 	@sentence: single world or sentence. 
# Return:
# 	vader sentiment
##########################

def print_sentiment_scores(sentence):
    snt = analyser.polarity_scores(sentence)
    return snt

##########################
# Check if word is a pronoun.
# Parameter:
# 	@item: string word.
# Return:
# 	True if the word is a pronoun;
#	False otherwise.
##########################

def isPRP(item):
	if not isinstance(item, list):
		tag = pos_tag([item])[0]
		if(tag[1] == 'PRP' or tag[1] == 'PRP$'):
			return True
	return False

##########################
# Check if word is verb.
# Parameter:
# 	@item: single string word. 
#	@tags: list of all words in the morphological tree with their label. Ex. [(have, VB)]
# Return:
# 	True if the word is a verb;
#	False otherwise.
##########################

def isVerb(item,tags):
	if not isinstance(item, list):

		tag = pos_tag([item])[0]
		for t in tags:
			if t[0] == tag[0]:
				if t[1] == 'VB' or t[1] == 'VBD' or t[1] == 'VBG' or t[1] == 'VBN' or t[1] == 'VBP' or t[1] == 'VBZ' or t[1] == 'MD':
					return True
	return False

##########################
# Check if word is 'each' or 'other'.
# Parameter:
# 	@word: string word.
# Return:
# 	True if the word is 'each' or 'other';
#	False otherwise.
##########################

def isEachOther(item):
	tag = pos_tag([item])[0]
	if(tag[0] == 'each' or tag[0] == 'other'):
		return True
	return False

##########################
# Method for extracting names, adjectives, adverbs, verbs, conjunctions and pronouns inside the morphological tree generated by the dream report.
# Parameters:
# 	@parent: root of the morphological tree representing the dream report;
# 	@subj: list in which to insert the extracted elements.
# Return:
# 	List of extracted elements
##########################

def getNodes(items):
	res =[]
	for node in items:
		if node[1] == 'NN' or node[1] == 'CC' or node[1] == 'PRP' or node[1] == 'POS' or node[1] == 'NNS' or node[1] == 'JJ' or node[1] == 'VBN' or node[1] == 'VB' or node[1] == 'VBD' or node[1] == 'VBG' or node[1] == 'VBN' or node[1] == 'VBP' or node[1] == 'VBZ' or node[1] == 'MD' or node[1] == 'TO' or node[1] == 'DT' or node[1] == 'NNPS' or node[1] == 'RP' or node[1] == 'RB':
			res.append(node[0])
		elif  node[1] == 'NNP':
			res.append(node[0]+'NNP')
	return res

##########################
# Clean results and return only the codes.
# Parameter:
# 	@items: list of aggression with characters.
# Return:
# 	List of coded aggression.
##########################

def clean(items):
	res = []
	for item in items:
		char1 = item.split(' - ')[0]
		char2 = item.split(' - ')[2]
		if '(' in char1:
			char1 = char1.split(' (')[1].replace(')','')
		if '(' in char2:
			char2 = char2.split(' (')[1].replace(')','')
		if 'I D' in char1:
			char1 = 'D'
		if 'I D' in char2:
			char2 = 'D'
		res.append(char1+' 4> '+char2)
	return res

##########################
# Check if verb is in 'verb_contact.txt'.
# Parameter:
# 	@item: single string word. 
#	@tags: list of all words in the morphological tree with their label. Ex. [(have, VB)]
# Return:
# 	result string with code, verb and sentiment score if verb is in 'contact_verb.txt';
#	'' otherwise.
##########################

def matchVerb(verb):
	score = print_sentiment_scores(verb)['compound']
	lemmatizer = WordNetLemmatizer()
	verb = lemmatizer.lemmatize(verb, 'v')
	file = open('verb_contact.txt','r',encoding='utf-8')
	list_one = file.read().split('\n')
	for x in list_one:
		verb_contact = x.strip('\n').split('\t')[0]
		code = x.strip('\n').split('\t')[1]
		if (verb == verb_contact):
			return code+' '+verb+' '+str(score)
	return ''

##########################
# Take the last male character from a list of characters, avoiding the 'char' character.
# Parameter:
# 	@lista: list of characters;
#	@char: string character to avoid.
# Return:
# 	The code of the character extracted from 'lista' or '1MSA' if there is no male character.
##########################

def takeLastMan(lista,char):
	split_list = []
	for i in range(len(lista)):
		if 'he ' in lista[i].lower() or 'his ' in lista[i].lower():
			split_list = lista[:i]
	if split_list != []:
		for k in reversed(split_list):
			if '1M' in k or '1I' in k and k != char:
				lista.remove(lista[i])
				return k
	return '1MSA'

##########################
# Take the last character from a list of characters.
# Parameter:
# 	@lista: list of characters;
# Return:
# 	The couple ('I D', the character extracted from 'lista' or 'Q' if there is no character).
##########################
		
def takeLast(lista):
	char2 = 'Q'
	for k in reversed(lista):
		if 'we ' not in k.lower() and 'We ' not in k and ' D' not in k.lower() and 'myself ' not in k.lower() and 'me ' not in k.lower() and 'my ' not in k.lower():
			char2 = k
			break
	return 'I D', char2


##########################
# Take the last female character from a list of characters, avoiding the 'char' character.
# Parameter:
# 	@lista: list of characters;
#	@char: string character to avoid.
# Return:
# 	The code of the character extracted from 'lista' or '1FSA' if there is no female character.
##########################

def takeLastFemale(lista,char):
	split_list = []
	for i in range(len(lista)):
		if 'she ' in lista[i].lower() or 'her ' in lista[i].lower():
			split_list = lista[:i]
	if split_list != []:
		for k in reversed(split_list):
			if '1F' in k or '1I' in k and k != char:
				lista.remove(lista[i])
				return k
	return '1FSA'

##########################
# Take the last group of characters from a list of characters, avoiding the 'char' group of characters.
# Parameter:
# 	@lista: list of characters;
#	@char: group of characters to avoid.
# Return:
# 	The code of the character extracted from 'lista' or '2ISA' if there is no group of characters.
##########################

def takeLastGroup(lista,char):
	split_list = []
	for i in range(len(lista)):
		if 'they ' in lista[i].lower():
			split_list = lista[:i]
	if split_list != []:
		for k in reversed(split_list):
			if '2' in k and k != char:
				lista.remove(lista[i])
				return k
	return '2ISA'

##########################
# Removes element in a list.
# Parameter:
# 	@item: item to delete.
# Return:
# 	List without all item.
##########################

def remove(item):
    final_list = []
    for num in duplicate:
        if num not in final_list:
            final_list.append(num)
    return final_list

##########################
# Codes characters following rules in https://dreams.ucsc.edu/Coding/characters.html and in https://dreams.ucsc.edu/Coding/aggression.html
# Parameter:
# 	@characters: list of possible characters. Ex. [['guy'],[Paolo]]
# Return:
# 	list of coded characters.
##########################

def code(characters):
	result = []
	last = ''
	p = inflect.engine()
	for items in characters:
		if items == [''] or items == []:
			continue
		if (len(items)==1):
			if items[0] == 'I':
					result.append(items[0]+' D')
			elif isPRP(items[0]):
					result.append(items[0]+' PRP')
			elif CharacterFrequency(items[0].replace('NNP','').replace('nnp','')):
				if len(items[0]) == 1:
					return []
				elif (isEachOther(items[0])):
					result.append(items[0])
				else:
					item = items[0].replace('nnp','').replace('NNP','')
					p = inflect.engine()
					lowerword=item.lower()
					if(p.singular_noun(item)):
						lowerword = p.singular_noun(item).lower()
					if(isAnimal(item) and not isAPerson(item)):
						if(isPlural(item)):
							result.append(item+' (2ANI)')
						else:
							result.append(item+' (1ANI)')
					elif(isAPerson(item) and not p.singular_noun(item) or isEthnic(item)):
						string = ' (1'
						if(isPlural(item)):
							string = ' (2'
						if(isOccupational(item)):
							string = string+'I'
						elif(gender(item) == False): 
							string = string+'M'
						elif(gender(item) == 15):
							string = string+'I'
						else:
							string = string+'F'
						if(isOccupational(item)):
							string = string+'O'
						elif(isEthnic(item)):
							string = string+'E'
						elif(lowerword in dictionary):	
							string = string+dictionary[lowerword]
						else:
							string = string+'K'
						if(lowerword == 'child' or lowerword == 'kid'):
							string = string+'C)'
							result.append(item+string)
						elif(lowerword == 'baby'):
							string = string+'B)'
							result.append(item+string)
						else:
							string = string+'A)'
							result.append(item+string)
					elif(isAGroup(item)):
						string = ' (2I'
						if(lowerword in dictionary):	
							string = string+dictionary[lowerword]
						elif(isEthnic(item)):
							string = string+'E'
						elif(isOccupational(item)):
							string = string+'O'
						else:
							string = string+'K'
						if(lowerword == 'child' or lowerword == 'kid'):
							string = string+'C)'
							result.append(item+string)
						elif(lowerword == 'baby'):
							string = string+'B)'
							result.append(item+string)
						else:
							string = string+'A)'
							result.append(item+string)
					elif(isUndefined(item)):
						if(isPlural(item)):
							string = ' (2'
						else:
							string = ' (1'
						if(gender(item) == False):
							string = string+'M'
						elif(gender(item) == 15):
							string = string+'I'
						else: 
							string = string+'F'
						if(lowerword in dictionary):	
							string = string+dictionary[lowerword]
						elif(isEthnic(item)):
							string = string+'E'
						elif(isOccupational(item)):
							string = string+'O'
						else:
							string = string+'K'
						if(lowerword == 'child' or lowerword == 'kid'):
							string = string+'C)'
							result.append(item+string)
						elif(lowerword == 'baby'):
							string = string+'B)'
							result.append(item+string)
						else:
							string = string+'A)'
							result.append(item+string)
					elif(isImaginary(item)):
						if(isPlural(item)):
							string = ' (6'
						else:
							string = ' (5'
						if(gender(item) == False):
							string = string+'M'
						elif(gender(item) == 15):
							string = string+'I'
						else: 
							string = string+'F'
						if(lowerword in dictionary):	
							string = string+dictionary[lowerword]
						elif(isEthnic(item)):
							string = string+'E'
						elif(isOccupational(item)):
							string = string+'O'
						else:
							string = string+'K'
						if(lowerword == 'child' or lowerword == 'kid'):
							string = string+'C)'
							result.append(item+string)
						elif(lowerword == 'baby'):
							string = string+'B)'
							result.append(item+string)
						else:
							string = string+'A)'
							result.append(item+string)
					elif(isDead(item)):
						if(isPlural(item)):
							string = ' (4'
						else:
							string = ' (3'
						if(gender(item) == False):
							string = string+'M'
						elif(gender(item) == 15):
							string = string+'I'
						else: 
							string = string+'F'
						if(lowerword in dictionary):	
							string = string+dictionary[lowerword]
						elif(isEthnic(item)):
							string = string+'E'
						elif(isOccupational(item)):
							string = string+'O'
						else:
							string = string+'K'
						if(lowerword == 'child' or lowerword == 'kid'):
							string = string+'C)'
							result.append(item+string)
						elif(lowerword == 'baby'):
							string = string+'B)'
							result.append(item+string)
						else:
							string = string+'A)'
							result.append(item+string)
		else:
			
			for item in items:
				if type(item) is list:
					item = ''

				lowerword=item.lower().replace('nnp','')
				if(p.singular_noun(item)):
					lowerword = p.singular_noun(item).lower()
	
				if not (isAPerson(item.replace('NNP','').replace('nnp','')) or isAnimal(lowerword) or isUndefined(lowerword) or isAGroup(lowerword) or lowerword == 'and' or lowerword in dead_words or lowerword in imaginary_words or lowerword in changed_words or item == 'I' or code([[lowerword]]) != []) and not CharacterFrequency(lowerword):

					items.remove(item)

			for i in range(0,len(items)):
				if items[i] == []:
					items[i] = ''

			if 'and' in items and len(items)>2:
				if 'I' in items:

					items.remove('and')
					items.remove('I')
					if CharacterFrequency(items[0].replace('NNP','').replace('nnp','')):
						cod = code([[items[0]]])
						if cod != []:
							result.append(cod[0])
				else:
					string=' (2'
					if deadGroup(items):
						string = ' (4'
						string = string+defineGenderGroup(items)
						string = string+'K' 
						string = string+'A)' 
						result.append((' '.join(items)+' '+'dead'+string).replace('NNP',''))
					elif imaginaryGroup(items):
						string = ' (6'
						string = string+defineGenderGroup(items)
						string = string+'K' 
						string = string+'A)' 
						result.append((' '.join(items)+' '+'imaginary'+string).replace('NNP',''))
					else:
						items.remove('and')
						string = string+defineGenderGroup(items)
						string = string+'K' 
						string = string+'A)'
						result.append((' '.join(items)+' '+string).replace('NNP',''))
			elif('and' in items and len(items)>1):
			
				items.remove('and')
				if CharacterFrequency(items[0].replace('NNP','').replace('nnp','')):
					cod = code([[items[0]]])
					if cod != []:
						result.append(cod[0])

			else:	
				for k in items:
					if(makeSingularAndLower(k) in dead_words):
						if (isPlural(k)):
							string = ' (4'
						else:
							string = ' (3'
						sub = items[0]
						items.remove(k)
						if(isOccupational(sub)):
							string = string+'I'
						elif(gender(sub) == False): 
							string = string+'M'
						elif(gender(item) == 15):
							string = string+'I'
						else:
							string = string+'F'
						string = string+'K'
						string = string+'A)'
						result.append((' '.join(items)+' '+k+string).replace('NNP',''))
					if(makeSingularAndLower(k) in imaginary_words):
						if (isPlural(k)):
							string = ' (6'
						else:
							string = ' (5'
						sub = items[0]
						items.remove(k)
						
						if(isOccupational(sub)):
							string = string+'I'
						elif(gender(sub) == False): 
							string = string+'M'
						elif(gender(item) == 15):
							string = string+'I'
						else:
							string = string+'F'
						string = string+'K'
						string = string+'A)' 
						result.append((' '.join(items)+' '+k+string))
					if(makeSingularAndLower(k) in changed_words):
						items.remove(k)
						form1 = code([[items[0]]])
						if '1' in form1[0]:
							res1 = form1[0].replace('1','7')
						else:
							res1 = form1[0].replace('2','7')
						result.append(res1)
						try:
							form2 = code([[items[1]]])
							if '1' in form1[0]:
								res2 =  form2[0].replace('1','8')
							else:
								res2 = form2[0].replace('2','8')
							result.append(res2)
						except:
							pass
	return result

##########################
# Extraction and encoding of friendliness interactions within dream reports 
# Parameter:
# 	@text: dream report.
# Return:
# 	list of clean coded friendliness interaction.
##########################

def friendliness_code(text, stanford_parser, nlp):

	result = []
	final_code = []
	#nlp = spacy.load('en_core_web_sm')
	doc=nlp(text)

	text = text.replace(',','').replace('!','').replace("I'm","I am").replace("you're","you are").replace("You're","You are").replace("we're","we are").replace("We're","We are").replace("they're","they are").replace("They're","They are").replace('(','').replace(')','').replace("He's","He is").replace("he's","he is").replace("She's","She is").replace("she's","she is").replace("It's","It is").replace("it's","it is").replace("'"," ").replace("\""," ").replace(';','').replace(':','')


	senteces = tokenize.sent_tokenize(text)
	characters = []
	for s in senteces:
		
		items = pos_tag(str(s.replace('.','')).split())

		sent_result = []
		result = []

		subject = []
		left = []
		right = []
		subject= getNodes(items)

		characters = characters + character_code(s, stanford_parser)
		interactions = []

		for i in range(len(subject)):
			flag = False

			aggcode = matchVerb(subject[i])

			if aggcode != '' and ('F' in aggcode):
				if pos_tag(subject[i])[1] == 'VBD' or pos_tag(subject[i])[1] == 'VBN':
					flag = True
				left = subject[:i][::-1]
				right = subject[i:]

				code1Char = []
				code2Char = []
				for x in left:
					code1Char = code([[x]])
					if code1Char != []:
						break
				for y in right:
					code2Char = code([[y]])
					if code2Char != []:
						break
				if code1Char == []:
					code1Char = 'Q'
				else:
					code1Char = code1Char[0]
				if code2Char == []:
					code2Char = 'Q'
				else:
					code2Char = code2Char[0]
				if 'we ' in code1Char.lower() or 'us ' in code1Char.lower():
					code1Char, code2Char = takeLast(characters)
				if 'myself ' in code1Char.lower() or 'me ' in code1Char.lower() or 'my ' in code1Char.lower():
					code1Char = 'I D'
				if 'they ' in code1Char.lower() or 'them ' in code1Char.lower():
					code1Char = takeLastGroup(characters,code2Char)
				if 'she ' in code1Char.lower() or 'her ' in code1Char.lower():
					code1Char = takeLastFemale(characters,code2Char)
				if 'he ' in code1Char.lower() or 'his ' in code1Char.lower():
					code1Char = takeLastMan(characters,code2Char)
				if 'myself ' in code2Char.lower() or 'me ' in code2Char.lower() or 'my ' in code2Char.lower():
					code2Char = 'I D'
				if 'they ' in code2Char.lower() or 'them ' in code2Char.lower():
					code2Char = takeLastGroup(characters,code1Char)
				if 'she ' in code2Char.lower() or 'her ' in code2Char.lower():
					code2Char = takeLastFemale(characters,code1Char)
				if 'he ' in code2Char.lower() or 'his ' in code2Char.lower():
					code2Char = takeLastMan(characters,code1Char)
				if not flag:
					interactions.append(code1Char+' - '+aggcode+' - '+code2Char)
				if flag:
					interactions.append(code2Char+' - '+aggcode+' - '+code1Char)

		for k in interactions:
			final_code.append(k)


	return clean(final_code)
