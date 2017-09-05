//
//  botFunctions.h
//  botForSimulator
//
//  Created by Anton Chumachenko on 27.08.17.
//  Copyright © 2017 Anton Chumachenko. All rights reserved.
//

#ifndef bot_functions_h
#define bot_functions_h

enum Erank {Ace, Two, Three, Four, Five, Six, Seven, Eight, Nine, Ten, Jack, Queen, King};
enum Esuit {Clubs, Diamonds, Hearts, Spikes};

class Cards
{
    
    int value;
public:
    Cards(int x = 0)
    {
        value = x;
    }
    
    Cards(string c)
    {
        int s, m;
        s = -1;
        m = 0;
        switch (c[1])
        {
            case '2':{ s = 0; break; }
            case '3':{ s = 1; break; }
            case '4':{ s = 2; break; }
            case '5':{ s = 3; break; }
            case '6':{ s = 4; break; }
            case '7':{ s = 5; break; }
            case '8':{ s = 6; break; }
            case '9':{ s = 7; break; }
            case 'T':{ s = 8; break; }
            case 'J':{ s = 9; break; }
            case 'Q':{ s = 10; break; }
            case 'K':{ s = 11; break; }
            case 'A':{ s = 12; break; }
        }
        
        char a = c[0];
        switch (a)
        {
            case 'C':{ m = 0; break; }
            case 'D':{ m = 1; break; }
            case 'H':{ m = 2; break; }
            case 'S':{ m = 3; break; }
        }
        
        value = m * 13 + s;
    }
    
    Erank getRank()
    {
        return Erank(value % 13);
    }
    
    
    
    Esuit getSuit()
    {
        return Esuit(value / 13);
    }
    
    int getValue()
    {
        return value;
    }
    
    string getstring()
    {
        int c = value % 13;
        int m = value / 13;
        string str = "";
        switch (c)
        {
            case 0:{str += '2'; break;}
            case 1:{str += '3'; break;}
            case 2:{str += '4'; break;}
            case 3:{str += '5'; break;}
            case 4:{str += '6'; break;}
            case 5:{str += '7'; break;}
            case 6:{str += '8'; break;}
            case 7:{str += '9'; break;}
            case 8:{str += 'T'; break;}
            case 9:{str += 'J'; break;}
            case 10:{str += 'Q'; break;}
            case 11:{str += 'K'; break;}
            case 12:{str += 'A'; break;}
        }
        
        switch (m)
        {
            case 0:{str += 'c'; break;}
            case 1:{str += 'd'; break;}
            case 2:{str += 'h'; break;}
            case 3:{str += 's'; break;}
        }
        
        return str;
    }
};

#endif /* bot_functions_h */
