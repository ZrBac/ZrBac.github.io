---
title: leetcode 647 palindromic substrings
date: 2019-12-20 15:11:05
tags:
- Java
categories: leetcode
---

### leetcode 647 palindromic substrings

Given a string, your task is to count how many palindromic substrings in this string.

The substrings with different start indexes or end indexes are counted as different substrings even they consist of same characters.

**Example 1:**

```
Input: "abc"
Output: 3
Explanation: Three palindromic strings: "a", "b", "c".
```

 

**Example 2:**

```
Input: "aaa"
Output: 6
Explanation: Six palindromic strings: "a", "a", "a", "aa", "aa", "aaa".
```

---

<!--more-->

#### solution one

`expand around center`

```java
class Solution{
    public int countSubstrings(String s) {
        int res = 0;
        int n = s.length();
        for (int i= 0; i < n; i++){
            for (int j = 0; i-j >= 0 && i+j < n && s.charAt(i-j) == s.charAt(i+j); j++)
                res++;
            for (int j = 0; i-j-1 >= 0 && i+j < n && s.charAt(i-j-1) == s.charAt(i+j); j++)
                res++;
        }
    }
    return res;
}
```

---

#### solution two

`dp`

```java
class Solution {
    public int countSubstrings(String s) {
        int res = 0;
        int n = s.length();
        boolean dp[][] = new boolean[n][n];
        for (int i = 0; i < n; i++) {
            for ( int j = i; j >= 0; j--) {
                dp[i][j] = (s.charAt(i) == s.charAt(j)) && (i-j < 3 || dp[i-1][j+1]);
                if (dp[i][j]){
                    res++;
                }
            }
        }
        return res;
    }
}
```

