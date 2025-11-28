from pymongo import MongoClient
from utils.config import Config

class Database:
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI)
        self.db = self.client.commerceboost
    
    def get_collection(self, collection_name):
        return self.db[collection_name]
    
    # Collections principales
    @property
    def users(self):
        return self.get_collection('users')
    
    @property
    def subscriptions(self):
        return self.get_collection('subscriptions')
    
    # Ajoutez cette collection à la classe Database :

    @property
    def referrals(self):
        return self.get_collection('referrals')

    @property
    def referrals(self):
        return self.get_collection('referrals')

    @property
    def payments(self):
        return self.get_collection('payments')
    
    @property
    def conversations(self):
        return self.get_collection('conversations')
    
    @property
    def promotions(self):
        return self.get_collection('promotions')
    
    @property
    def margin_calculations(self):
        return self.get_collection('margin_calculations')
    
    # Collections contenu
    @property
    def predefined_tips(self):
        return self.get_collection('predefined_tips')
    
    @property
    def predefined_promos(self):
        return self.get_collection('predefined_promos')
    
    @property
    def inspirational_stories(self):
        return self.get_collection('inspirational_stories')
    
    @property
    def motivation_messages(self):
        return self.get_collection('motivation_messages')

# Instance globale
db = Database()