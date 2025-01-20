from itertools import product


class Solution:


    def TwoSum(t:int, a:list[int]):
        if 2 >= len(a) >= 10**4:        #ограничения
            return []
        if -10**9 >= t >= 10**9:       #ограничения
            return[]
        g = a
        f = a
        my_set = []
        for i,val1 in enumerate(g):
            for j,val2 in enumerate(f[i:]):         #Проход по всем значениям списка
                if -10**9 >= f[j] >= 10**9:         #ограничения
                    return[]
                if i in my_set or j+i in my_set or i == j+i:    #Отсеивание тех чисел которые уже использовались
                        continue
                else:
                    if val1 + val2 == t:                    #Основная проверка на равенство
                        my_set.append(i)
                        my_set.append(j+i)     
                        break
        return my_set            
                    
        
f = [2, 7, 11, 15]
t = 9
r = Solution
print(r.TwoSum(t, f))

f = [3,2,4]
t = 6
print(r.TwoSum(t, f))

f = [3,3]
t = 6
print(r.TwoSum(t, f))

f = [3,3,2,5,4,1,3,4,7,1,2]
t = 9
print(r.TwoSum(t, f))
