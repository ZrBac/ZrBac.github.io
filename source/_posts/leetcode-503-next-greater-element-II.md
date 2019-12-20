---
title: leetcode 503 next greater element II
date: 2019-12-20 15:07:51
tags:
- Java
categories: leetcode
---

### leetcode 503 next greater element II

Given a circular array (the next element of the last element is the first element of the array), print the Next Greater Number for every element. The Next Greater Number of a number x is the first greater number to its traversing-order next in the array, which means you could search circularly to find its next greater number. If it doesn't exist, output -1 for this number.

**for example:**

```
Input: [1,2,1]
Output: [2,-1,2]
Explanation: The first 1's next greater number is 2; The number 2 can't find next greater number; The second 1's next greater number needs to search circularly, which is also 2.
```

---

#### solution one 

`brute force`

```java
public class Solution {
    public int[] nextGreaterElements(int[] nums) {
        int n = nums.length;
        int[] res = new int[n];
        for (int i = 0; i < n; i++){
            res[i] = -1;
            for (int j = 1; j < n; j++){
                if (nums[(i + j) % n] > nums[i]){
                    res[i] = nums[(i + j) % n];
                    break;
                }
            }
        }
        return res;
    }
}
```

---

#### solution two

`stack`

```java
public class solution{
    public int[] nextGreaterElements(int[] nums) {
        int n = nums.length;
        int[] res = new int[n];
        Stack<Integer> stack = new Stack();
        for (int i = 2*n-1; i >= 0; i--) {
            while (!stack.empty() && nums[stack.peek()] <= nums[i % n]) {
                stack.pop();
            }
            res[i % n] = stack.empty() ? -1 : nums[stack.peek()];
            stack.push(i % n);
        }
        return res;
    }
}
```

