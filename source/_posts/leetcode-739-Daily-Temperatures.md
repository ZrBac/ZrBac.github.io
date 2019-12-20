---
title: leetcode 739 Daily Temperatures
date: 2019-12-20 15:12:36
tags:
- Java
categories: leetcode
---

### leetcode 739 :Daily Temperatures

Given a list of daily temperatures `T`, return a list such that, for each day in the input, tells you how many days you would have to wait until a warmer temperature. If there is no future day for which this is possible, put `0` instead.

For example, given the list of temperatures `T = [73, 74, 75, 71, 69, 72, 76, 73]`, your output should be `[1, 1, 4, 2, 1, 1, 0, 0]`.

#### solution one

`list`,process each `i` in reverse order.

```java
class Solution {
    public int[] dailyTemperatures(int[] T) {
        int n = T.length;
        int[] ans = new int[n];
        int[] next = new int[101];
        Arrays.fill(next, Integer.MAX_VALUE);
        for(int i=n-1;i>=0;i--){
            int hotter = Integer.MAX_VALUE;
            for(int j=T[i]+1;j<=100;j++){
                if(next[j]<hotter)
                    hotter = next[j];
            }
            if(hotter<Integer.MAX_VALUE){
                ans[i] = hotter - i;
            }
            
            next[T[i]] = i;
                           
        }
        return ans;
    }
}
```



#### solution two

`stack`, reverse order, remember a list of indices representing a strictly increasing list of tempertures, the top of the stack is the first value in the list at last.

```java
class Solution {
    public int[] dailyTemperatures(int[] T) {
        int[] ans = new int [T.length];
        int n = T.length;
        Stack<Integer> stack = new Stack();
        for(int i = n-1; i>= 0; i--){
            while(!stack.isEmpty()&&T[i]>=T[stack.peek()])
                stack.pop();
            if(stack.isEmpty())
                ans[i] = 0;
            else
                ans[i] = stack.peek() - i;
            stack.push(i);
        }
        return ans;
    }
}
```
