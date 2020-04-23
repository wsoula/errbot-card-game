from errbot import BotPlugin, botcmd, arg_botcmd, re_botcmd
import urllib.request
import json

class Cards(BotPlugin):
    """Simple card game that just returns cards"""

    @arg_botcmd('-c',dest='total_cards',type=str,default='1')
    @arg_botcmd('command',type=str)
    def card(self,msg,command=None,total_cards=1):
        # For new actions get a new deck, otherwise the deck_id is stored in /tmp/deck_id
        if command == 'new':
            deck_id=self.get_deck()
            f = open('/tmp/deck_id','w')
            f.write(deck_id)
            f.close()
            #print('deck_id='+deck_id)
        else:
            f = open('/tmp/deck_id','r')
            # Remove trailing newline
            deck_id=f.read().splitlines()[0]
            f.close()
        # Now that we have the deck_id determine what to do with it
        if command == 'draw':
            card=self.get_card(deck_id,total_cards)
            return card
        if command == 'status':
            remaining=self.get_status(deck_id)
            return(str(remaining)+' cards remaining')
        if command == 'shuffle':
            remaining=self.shuffle_deck(deck_id)
            return('Shuffled.  '+str(remaining)+' cards remaining')

    def get_deck(self):
        deck_response=self.get_url('https://deckofcardsapi.com/api/deck/new/shuffle/')
        return deck_response['deck_id']

    def get_card(self,deck_id,total_cards):
        #drawn_cards=[]
        card_response=self.get_url('https://deckofcardsapi.com/api/deck/'+deck_id+'/draw/?count='+total_cards)
        # Spaces get squashed in slack, and it adds a ` character to the beginning and end
        line_default_top='     ┌─────────┐ '
        line_default_two='     │{} {}                 │ '
        line_default_blank='     │                          │ '
        line_default_middle='     │           {}         │ '
        line_default_penultimate='     │                 {} {}│ '
        line_default_bottom='     └─────────┘ '
        line_final_two=''
        line_final_middle=''
        line_final_penultimate=''
        length=len(card_response['cards'])
        for card in card_response['cards']:
            card_number=card['value']
            card_suit=card['suit']
            if card_suit == 'DIAMONDS':
                suit='\u2666'
            elif card_suit == 'HEARTS':
                suit='\u2665'
            elif card_suit == 'SPADES':
                suit='\u2660'
            elif card_suit == 'CLUBS':
                suit='\u2663'
            else:
                print(card_suit+' is not a valid suit')
                exit(1)
            line_final_two+=line_default_two.format(card_number[0],suit)
            line_final_middle+=line_default_middle.format(suit)
            line_final_penultimate+=line_default_penultimate.format(card_number[0],suit)
            #drawn_cards.append({'number':card_number,'suit':suit})
        formatted_card ="""```
{}
{}
{}
{}
{}
{}
{}
{}
{}""".format(line_default_top*length,line_final_two,line_default_blank*length,line_default_blank*length,line_final_middle,line_default_blank*length,
             line_default_blank*length,line_final_penultimate,line_default_bottom*length)
        return formatted_card[1:]

    def get_status(self,deck_id):
        deck_response=self.get_url('https://deckofcardsapi.com/api/deck/'+deck_id+'/')
        return deck_response['remaining']

    def shuffle_deck(self,deck_id):
        deck_response=self.get_url('https://deckofcardsapi.com/api/deck/'+deck_id+'/shuffle/')
        return deck_response['remaining']

    def get_url(self,url):
        page = urllib.request.Request(url,headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(page).read().decode('utf-8')
        return json.loads(response)
