from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk

class Analyzer:
    def __init__(self, language="english", sentences_count=5):
        self.language = language
        self.sentences_count = sentences_count
        self.summarizer = LsaSummarizer()
        self.summarizer.stop_words = get_stop_words(language)
        
        # Ensure NLTK data is available (sometimes needed for tokenizer)
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            nltk.download('punkt_tab')

    def summarize(self, text):
        """
        Returns a summary string of the provided text.
        """
        if not text or len(text.split()) < 50:
            return text  # Too short to summarize, return as is

        parser = PlaintextParser.from_string(text, Tokenizer(self.language))
        summary_sentences = self.summarizer(parser.document, self.sentences_count)
        
        summary = " ".join([str(sentence) for sentence in summary_sentences])
        return summary

    def get_key_points(self, text, count=5):
        """
        Returns a list of key sentences (bullet points).
        """
        if not text or len(text.split()) < 30:
            return [text] if text else []

        parser = PlaintextParser.from_string(text, Tokenizer(self.language))
        summary_sentences = self.summarizer(parser.document, count)
        
        return [str(sentence) for sentence in summary_sentences]

    def get_narrative_block(self, text, sentence_count=15):
        """
        Returns a cohesive block of text.
        Mode: SEO (aims for ~100+ words).
        """
        if not text: return ""
        
        parser = PlaintextParser.from_string(text, Tokenizer(self.language))
        summary_sentences = self.summarizer(parser.document, sentence_count)
        
        block = " ".join([str(sentence) for sentence in summary_sentences])
        
        # Simple check: if block is too short, double it (simulation of 'write more')
        if len(block.split()) < 50:
            block += " " + block
            
        return block

    def generate_faq_answers(self, text):
        # Naive FAQ generation from text
        # Real impl would use an LLM, here we extract sentences
        return self.get_narrative_block(text, 3)

    def generate_executive_summary(self, all_texts):
        """
        Generates a master summary from a large collection of texts.
        """
        combined_text = " ".join(all_texts)
        # Limit processing for speed and memory
        if len(combined_text) > 100000:
            combined_text = combined_text[:100000]
            
        parser = PlaintextParser.from_string(combined_text, Tokenizer(self.language))
        # Get more sentences for the master summary
        summary_sentences = self.summarizer(parser.document, 10)
        
        return [str(s) for s in summary_sentences]
