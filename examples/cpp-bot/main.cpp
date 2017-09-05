#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <ctime>
#include <fstream>
#include <sstream>
#include "unistd.h"

#include "rapidjson/document.h"
#include "rapidjson/reader.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"

using namespace std;
using namespace rapidjson;

#include "poker_math.h"
#include "bot_functions.h"

const int countHoleCards = 2;
const int countCommunityCards = 5;
const int cardsInDeck = 52;

vector<Cards> myCards;
vector<Cards> communityCards;
vector<Cards> potencialOppCard;

struct MyAction
{
    string typeAction;
    int amount;
    
    MyAction()
    {
        
    }
    
    MyAction(string typeAction, int amount)
    {
        this->typeAction = typeAction;
        this->amount = amount;
    }
    
    void make()
    {
        cout << typeAction << "\t" << amount << endl;
    }
};

struct FastDeck
{
    int cardMask[cardsInDeck];
    
    void clear()
    {
        for (int i = 0; i < cardsInDeck; i++) cardMask[i] = 0;
    }
    
    void getCard(int i) {cardMask[i] = 1;}
    
    int getRandomCard()
    {
        int i;
        while (cardMask[i = rand() % cardsInDeck]) {};
        cardMask[i] = 1;
        return i;
    }
};

float calcWinrate(int countIteration)
{
    FastDeck deck;
    deck.clear();
    for (int i = 0; i < myCards.size(); i++) deck.getCard(myCards[i].getValue());
    for (int i = 0; i < communityCards.size(); i++) deck.getCard(communityCards[i].getValue());
    
    double pointWin = 0;
    
    for (int a = 0; a < countIteration; a++)
    {
        potencialOppCard.clear();
        vector<Cards> potentialCommunityCards = communityCards;
        FastDeck tempDeck = deck;
        for (int i = communityCards.size(); i < countCommunityCards; i++) potentialCommunityCards.push_back(tempDeck.getRandomCard());
        for (int i = 0; i < countHoleCards; i++) potencialOppCard.push_back(tempDeck.getRandomCard());
        
        int myVal = combinationF7(potentialCommunityCards[0].getRank(), potentialCommunityCards[0].getSuit(), potentialCommunityCards[1].getRank(), potentialCommunityCards[1].getSuit(), potentialCommunityCards[2].getRank(), potentialCommunityCards[2].getSuit(), potentialCommunityCards[3].getRank(), potentialCommunityCards[3].getSuit(), potentialCommunityCards[4].getRank(), potentialCommunityCards[4].getSuit(),
            myCards[0].getRank(), myCards[0].getSuit(),
            myCards[1].getRank(), myCards[1].getSuit());
        
        int oppVal = combinationF7(potentialCommunityCards[0].getRank(), potentialCommunityCards[0].getSuit(), potentialCommunityCards[1].getRank(), potentialCommunityCards[1].getSuit(), potentialCommunityCards[2].getRank(), potentialCommunityCards[2].getSuit(), potentialCommunityCards[3].getRank(), potentialCommunityCards[3].getSuit(), potentialCommunityCards[4].getRank(), potentialCommunityCards[4].getSuit(),
                                   potencialOppCard[0].getRank(), potencialOppCard[0].getSuit(),
                                   potencialOppCard[1].getRank(), potencialOppCard[1].getSuit());
        
        double result = 0.0;
        if (myVal > oppVal) result = 1.0;
        if (myVal == oppVal) result = 0.5;
        if (myVal < oppVal) result = 0.0;
        
        pointWin += result;
    }
    
    return pointWin / (countIteration);
}

void parse_declare_action(Document &jsonObj)
{
    
    myCards.clear();
    for (int i = 0; i < jsonObj["hole_card"].GetArray().Size(); i++)
    {
        myCards.push_back(Cards(jsonObj["hole_card"].GetArray()[i].GetString()));
    }
    
    communityCards.clear();
    for (int i = 0; i < jsonObj["round_state"]["community_card"].GetArray().Size(); i++)
    {
        communityCards.push_back(Cards(jsonObj["round_state"]["community_card"].GetArray()[i].GetString()));
    }
    
    potencialOppCard.clear();
    
    MyAction act("fold", 0);
    int maxRaise = 0;
    int callAmount = 0;
    
    Value &valid_actions = jsonObj["valid_actions"];
    for (int i = 0; i < valid_actions.GetArray().Size(); i++)
    {
        if (!strcmp(valid_actions.GetArray()[i]["action"].GetString(), "raise"))
        {
            maxRaise = valid_actions.GetArray()[i]["amount"]["max"].GetInt();
        }
        
        if (!strcmp(valid_actions.GetArray()[i]["action"].GetString(), "call"))
        {
            callAmount = valid_actions.GetArray()[i]["amount"].GetInt();
        }
    }
    
    double winRate = calcWinrate(3000);

    if (maxRaise > 0)
    {
        if (winRate > 0.6) act = MyAction("raise", maxRaise);
    }
    
    act.make();
}

void parse_game_start(Document &jsonObj)
{
    
}

void parse_round_start(Document &jsonObj)
{

}

void parse_street_start(Document &jsonObj)
{
    
}

void parse_game_update(Document &jsonObj)
{
    
}

void parse_round_result(Document &jsonObj)
{
    
}

int main(int argc, const char * argv[])
{
    srand(unsigned(time(NULL)));
    InitRankCombination();
    
   // ifstream cin("input.txt");

    // game loop
    while(1)
    {
        string typeAction, json;

        cin >> typeAction;
        getline(cin, json);
        
        Document jsonObj;
        jsonObj.Parse(json.c_str());
        
        if (typeAction == "declare_action") parse_declare_action(jsonObj);
        if (typeAction == "game_start") parse_game_start(jsonObj);
        if (typeAction == "round_start") parse_round_start(jsonObj);
        if (typeAction == "street_start") parse_street_start(jsonObj);
        if (typeAction == "game_update") parse_game_update(jsonObj);
        if (typeAction == "round_result") parse_round_result(jsonObj);
    }
    
    return 0;
}
