---
title: leetcode 10 regular expression matching
date: 2019-12-20 14:59:05
tags:
- Java
categories: leetcode
---

### leetcode 10 regular expression matching

Given an input string (`s`) and a pattern (`p`), implement regular expression matching with support for `'.'` and `'*'`.

```
'.' Matches any single character.
'*' Matches zero or more of the preceding element.
```

The matching should cover the **entire** input string (not partial).

<!--more-->

**Note:**

- `s` could be empty and contains only lowercase letters `a-z`.
- `p` could be empty and contains only lowercase letters `a-z`, and characters like `.` or `*`.

**Example 1:**

```
Input:
s = "aa"
p = "a"
Output: false
Explanation: "a" does not match the entire string "aa".
```

**Example 2:**

```
Input:
s = "aa"
p = "a*"
Output: true
Explanation: '*' means zero or more of the preceding element, 'a'. Therefore, by repeating 'a' once, it becomes "aa".
```

**Example 3:**

```
Input:
s = "ab"
p = ".*"
Output: true
Explanation: ".*" means "zero or more (*) of any character (.)".
```

**Example 4:**

```
Input:
s = "aab"
p = "c*a*b"
Output: true
Explanation: c can be repeated 0 times, a can be repeated 1 time. Therefore, it matches "aab".
```

**Example 5:**

```
Input:
s = "mississippi"
p = "mis*is*p*."
Output: false
```

---

#### solution one

`recursion`

```java
class Solution {
    public boolean isMatch(String s, String p) {
        if(p.isEmpty())
            return s.isEmpty();
        boolean first_match = (!p.isEmpty() && (p.charAt(0) == s.charAt(0) || 
                              p.charAt(0) == '.'));
        
        if(p.length >=2 && p.charAt(1) == '*') {
            return (isMatch(s, p.substring(2)) || 
                    (first_match && isMatch(s.substring(1),p)));
        }
        else {
            return first_match && isMatch(s.substring(1), p.substring(1));
        }
    }
}
```