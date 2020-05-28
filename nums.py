# python code
# import random module instead of creating the sample_one(arr) helper
import random

def single_round(N, L , P , index):
    # randomly chooses the start of the first trampoline
    tramp1_start = random.randint(1, N - L + 1)
    # create a list L long starting from tramp1_start to represent the numbers tramp1 is covering
    tramp1 = list(range(tramp1_start, tramp1_start + L))
    # same process for tramp2
    tramp2_start = random.randint(1, N - L + 1)
    tramp2 = list(range(tramp2_start, tramp2_start + L))
    # places gift at index of tramp1
    gift = tramp1[index]
    # randomly selects diver location between 1 and N
    diver = random.randint(1, N)
    # if diver landed on trampoline 2 return 1
    if diver in tramp2:
        return 1
    # if diver landed on trampoline 1:
    # rolls a random number and compares to P
    # return 5 if P is greater - meaning he landed on the gift
    elif diver in tramp1:
        if P >= random.random(0,1):
            return 5
        return 1
    # returns 0 if the diver missed both trampolines
    return 0

# main program calling on the single_round() function
print(single_round(10, 5, 0.3, 2))


# sum = (L/N)/(N-L+1)
# for i in range(L+1,N+1)
#     sum += (i/N)/(2*(N-i+1)/square(N-L+1))