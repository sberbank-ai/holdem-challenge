//
//  PokerMath.h
//  Poker-Simulator
//
//  Created by antmsu on 14.08.17.
//  Copyright © 2017 Hakaton. All rights reserved.
//

#ifndef poker_math_h
#define poker_math_h

#include <math.h>

int combination(int d[])
{
    int c[5];
    c[0] = d[0];
    c[1] = d[1];
    c[2] = d[2];
    c[3] = d[3];
    c[4] = d[4];
    double temp = 0;
    for (int j = 0; j < 5; j++)
        for (int i = j+1; i < 5; i++)
        {
            if (c[i] == c[j]) temp++;
        }
    
    if (temp == 10) return - 1;
    
    for (int j = 0; j < 5; j++)
        for (int i = 0; i < 4; i++)
        {
            int temp2 = 0;
            //       int temp3 = 0;
            if (c[i+1] < c[i])
            {
                temp2 = c[i];
                c[i] = c[i+1];
                c[i+1] = temp2;
            }
        }
    
    const int P[5] = {1, 13, 169, 169*13, 169*169};
    int k = 0;
    if ((temp == 6) || (temp == 4))
    {
        if (c[4] == c[2]) k = c[4]*P[1] + c[0];
        else k = c[2]*P[1] + c[4];
    }
    
    if (temp == 3)
    {
        if (c[4] == c[2]) k = c[4]*P[2] + c[1]*P[1] + c[0];
        if (c[3] == c[1]) k = c[3]*P[2] + c[4]*P[1] + c[0];
        if (c[2] == c[0]) k = c[2]*P[2] + c[4]*P[1] + c[3];
    }
    
    if (temp == 2)
    {
        if (c[4] != c[3]) k = c[3]*P[2] + c[1]*P[1] + c[4];
        if (c[0] != c[1]) k = c[3]*P[2] + c[1]*P[1] + c[0];
        if (c[2] != c[3]) k = c[3]*P[2] + c[1]*P[1] + c[2];
    }
    
    if (temp == 1)
    {
        if (c[4] == c[3]) k = c[4]*P[3] + c[2]*P[2] + c[1]*P[1] + c[0];
        if (c[3] == c[2]) k = c[3]*P[3] + c[4]*P[2] + c[1]*P[1] + c[0];
        if (c[2] == c[1]) k = c[2]*P[3] + c[4]*P[2] + c[3]*P[1] + c[0];
        if (c[1] == c[0]) k = c[1]*P[3] + c[4]*P[2] + c[3]*P[1] + c[2];
    }
    
    if (temp == 0)
    {
        k = c[4]*P[4] + c[3]*P[3] + c[2]*P[2] + c[1]*P[1] + c[0]*P[0];
    }
    
    if (temp == 6) temp = 7;
    if (temp == 4) temp = 6;
    if ((temp == 0) && (c[4] == 12) && (c[3] == 3) && (c[0] == 0)) {temp = 4; k = 1;}
    if ((temp == 0) && (c[4] - c[0] == 4)) temp = 4;
    
    return temp * 10000000 + k;
}



int ArrayRank[52] = {0,1,2,3,4,5,6,7,8,9,10,11,12,0,1,2,3,4,5,6,7,8,9,10,11,12,0,1,2,3,4,5,6,7,8,9,10,11,12,0,1,2,3,4,5,6,7,8,9,10,11,12};
int ArraySuite[52] = {0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3};

const int max_ = 13*13*13*13*13;
int Array[13][13][13][13][13];

void InitRankCombination()
{
    for (int i = 0; i < max_; i++)
    {
        int temp = i;
        int c[5];
        int d[5];
        for (int j = 0; j < 5; j++)
        {
            c[j] = temp % 13;
            temp = temp / 13;
        }
        if ((c[0] == 10) && (c[1] == 10))
        {
            //             int y = 0;
        }
        d[0] = c[0];
        d[1] = c[1];
        d[2] = c[2];
        d[3] = c[3];
        d[4] = c[4];
        Array[c[0]][c[1]][c[2]][c[3]][c[4]] = combination(d);
    }
}

inline int combinationF5(int cr1, int cs1, int cr2, int cs2, int cr3, int cs3, int cr4, int cs4, int cr5, int cs5)
{
    int f = 0;
    int sf = 0;
    if ((cs1 == cs2) && (cs2 == cs3) && (cs3 == cs4) && (cs4 == cs5)) f = 1;
    int Rank = Array[cr1][cr2][cr3][cr4][cr5];
    if (f == 1) return 50000000 + Rank;
    return Rank;
}

inline int combinationF7(int cr1, int cs1, int cr2, int cs2, int cr3, int cs3, int cr4, int cs4, int cr5, int cs5, int cr6, int cs6, int cr7, int cs7)
{
    int Comb[21];
    Comb[0] = combinationF5(cr1, cs1, cr2, cs2, cr3, cs3, cr4, cs4, cr5, cs5);
    Comb[1] = combinationF5(cr1, cs1, cr2, cs2, cr3, cs3, cr4, cs4, cr6, cs6);
    Comb[2] = combinationF5(cr1, cs1, cr2, cs2, cr3, cs3, cr5, cs5, cr6, cs6);
    Comb[3] = combinationF5(cr1, cs1, cr2, cs2, cr4, cs4, cr5, cs5, cr6, cs6);
    Comb[4] = combinationF5(cr1, cs1, cr3, cs3, cr4, cs4, cr5, cs5, cr6, cs6);
    Comb[5] = combinationF5(cr2, cs2, cr3, cs3, cr4, cs4, cr5, cs5, cr6, cs6);
    
    Comb[6] = combinationF5(cr1, cs1, cr2, cs2, cr3, cs3, cr4, cs4, cr7, cs7);
    Comb[7] = combinationF5(cr1, cs1, cr2, cs2, cr3, cs3, cr5, cs5, cr7, cs7);
    Comb[8] = combinationF5(cr1, cs1, cr2, cs2, cr4, cs4, cr5, cs5, cr7, cs7);
    Comb[9] = combinationF5(cr1, cs1, cr3, cs3, cr4, cs4, cr5, cs5, cr7, cs7);
    Comb[10] =combinationF5(cr2, cs2, cr3, cs3, cr4, cs4, cr5, cs5, cr7, cs7);
    
    Comb[11] = combinationF5(cr1, cs1, cr2, cs2, cr3, cs3, cr6, cs6, cr7, cs7);
    Comb[12] = combinationF5(cr1, cs1, cr2, cs2, cr4, cs4, cr6, cs6, cr7, cs7);
    Comb[13] = combinationF5(cr1, cs1, cr3, cs3, cr4, cs4, cr6, cs6, cr7, cs7);
    Comb[14] = combinationF5(cr2, cs2, cr3, cs3, cr4, cs4, cr6, cs6, cr7, cs7);
    
    Comb[15] = combinationF5(cr1, cs1, cr2, cs2, cr5, cs5, cr6, cs6, cr7, cs7);
    Comb[16] = combinationF5(cr1, cs1, cr3, cs3, cr5, cs5, cr6, cs6, cr7, cs7);
    Comb[17] = combinationF5(cr2, cs2, cr3, cs3, cr5, cs5, cr6, cs6, cr7, cs7);
    
    Comb[18] = combinationF5(cr1, cs1, cr4, cs4, cr5, cs5, cr6, cs6, cr7, cs7);
    Comb[19] = combinationF5(cr2, cs2, cr4, cs4, cr5, cs5, cr6, cs6, cr7, cs7);
    
    Comb[20] = combinationF5(cr3, cs3, cr4, cs4, cr5, cs5, cr6, cs6, cr7, cs7);
    
    int max = 0;
    
    if (Comb[0] > max) max = Comb[0];
    if (Comb[1] > max) max = Comb[1];
    if (Comb[2] > max) max = Comb[2];
    if (Comb[3] > max) max = Comb[3];
    if (Comb[4] > max) max = Comb[4];
    if (Comb[5] > max) max = Comb[5];
    if (Comb[6] > max) max = Comb[6];
    if (Comb[7] > max) max = Comb[7];
    if (Comb[8] > max) max = Comb[8];
    if (Comb[9] > max) max = Comb[9];
    if (Comb[10] > max) max = Comb[10];
    if (Comb[11] > max) max = Comb[11];
    if (Comb[12] > max) max = Comb[12];
    if (Comb[13] > max) max = Comb[13];
    if (Comb[14] > max) max = Comb[14];
    if (Comb[15] > max) max = Comb[15];
    if (Comb[16] > max) max = Comb[16];
    if (Comb[17] > max) max = Comb[17];
    if (Comb[18] > max) max = Comb[18];
    if (Comb[19] > max) max = Comb[19];
    if (Comb[20] > max) max = Comb[20];
    
    return max;
}


#endif /* poker_math_h */
