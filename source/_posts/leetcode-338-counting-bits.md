---
title: leetcode 338 counting bits
date: 2019-12-20 15:05:44
tags:
- Java
categories: leetcode
---

### leetcode 338 counting bits

Given a non negative integer number **num**. For every numbers **i** in the range **0 ≤ i ≤ num** calculate the number of 1's in their binary representation and return them as an array.

**Example 1:**

```
Input: 2
Output: [0,1,1]
```

**Example 2:**

```
Input: 5
Output: [0,1,1,2,1,2]
```

---

#### solution one

`easy to come up with`

```markdown
dp[0] = 0;
dp[1] = dp[0] + 1;
dp[2] = dp[0] + 1;
dp[3] = dp[1] + 1;
dp[4] = dp[0] + 1;
dp[5] = dp[1] + 1;
dp[6] = dp[2] + 1;
dp[7] = dp[3] + 1;
dp[8] = dp[0] + 1;
...
```

*this is overlap sub problem, and we can come up the DP solution*

```java
classs Solution {
    public int[] countBits(int num) {
        int[] res = new int[num+1];
        res[0] = 0;
        for (int i = 1; i <= num; i++)
            res[i] = res[i/2] + i%2;
        return res;
    }
}
```

---

#### solution two

```markdown
anthoer function(tricky one):
dp[0] = 0;
dp[1] = dp[1-1] + 1;
dp[2] = dp[2-2] + 1;
dp[3] = dp[3-2] +1;
dp[4] = dp[4-4] + 1;
dp[5] = dp[5-4] + 1;
dp[6] = dp[6-4] + 1;
dp[7] = dp[7-4] + 1;
dp[8] = dp[8-8] + 1;
...
```

*Obviously, we can find the pattern for above example, so now we get the general function*

**dp[index] = dp[index - offset] + 1;**

```java
public int[] countBits(int num) {
    int result[] = new int[num + 1];
    int offset = 1;
    for (int index = 1; index < num + 1; ++index){
        if (offset * 2 == index){
            offset *= 2;
        }
        result[index] = result[index - offset] + 1;
    }
    return result;
}
```

