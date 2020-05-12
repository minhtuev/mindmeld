import logging
import spacy

from .system_entity_recognizer import SystemEntityRecognizer, SystemEntityError

logger = logging.getLogger(__name__)


class SpacyRecognizer(SystemEntityRecognizer):
    _instance = None

    def __init__(self, model="en_core_web_md"):
        if not self._instance:
            logger.info("Loading spacy model %s.", model)
            self.nlp = spacy.load(model)
            self.model = model
            self._instance = self
        elif model != self._instance.model:
            self.nlp = spacy.load(model)
            self.model = model
            self._instance = self
        else:
            raise SystemEntityError("SpacyRecognizer follows a singleton pattern.")

    @staticmethod
    def get_instance(model):
        if not SpacyRecognizer._instance:
            SpacyRecognizer(model)
        return SpacyRecognizer._instance

    def parse(
        self,
        sentence,
        dimensions=None,
        language=None,
        locale=None,
        time_zone=None,
        timestamp=None,
    ):
        doc = self.nlp(sentence)
        entities = [
            {
                "body": ent.text,
                "start": ent.start_char,
                "end": ent.end_char,
                "value": {"value": ent.text},
                "dim": ent.label_,
            }
            for ent in doc.ents
        ]
        return entities, 200

    def get_candidates_for_text(
        self, text, entity_types=None, language=None, locale=None
    ):
        pass

    def get_candidates(
        self,
        query,
        entity_types=None,
        locale=None,
        language=None,
        time_zone=None,
        timestamp=None,
    ):
        pass

    def resolve_system_entity(self, query, entity_type, span):
        pass
