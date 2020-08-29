---
title: 剑指Offer题解（3-40）
date: 2020-08-27 15:13:08
tags:
- Java
categories: leetcode
---

## 剑指Offer题解（3-40）

#### [面试题03. 数组中重复的数字](https://leetcode-cn.com/problems/shu-zu-zhong-zhong-fu-de-shu-zi-lcof/)

找出数组中重复的数字。
在一个长度为 n 的数组 nums 里的所有数字都在 0～n-1 的范围内。数组中某些数字是重复的，但不知道有几个数字重复了，也不知道每个数字重复了几次。请找出数组中任意一个重复的数字。

 **示例 1：** 

```java
输入：
[2, 3, 1, 0, 2, 5, 3]
输出：2 或 3 
```

 **思路和代码：** 

```java
class Solution {
    public int findRepeateNumber(int[] nums) {
        for(int i=0; i<nums.length; i++) {	//如果当前值不是当前索引对应的值
            while(nums[i] != i) {
                int cur = nums[i];
                if(nums[cur] = cur)	//当前值对应的索引是否已经存有了当前值，如果是说明重复
                    return cur;
                else {			//如果不是，就将当前值放到自己对应的索引，将自己对应索引的值放过来
                    nums[i] = nums[cur];
                    nums[cur] = cur;
                }
            }
        }
        return 0;		//没找到，返回0（随便返回一个数即可）
    }
}
```


<!--more-->


#### [面试题04. 二维数组中的查找](https://leetcode-cn.com/problems/er-wei-shu-zu-zhong-de-cha-zhao-lcof/)

 在一个 n * m 的二维数组中，每一行都按照从左到右递增的顺序排序，每一列都按照从上到下递增的顺序排序。请完成一个函数，输入这样的一个二维数组和一个整数，判断数组中是否含有该整数。 

**示例:**

现有矩阵 matrix 如下：

```java
[
  [1,   4,  7, 11, 15],
  [2,   5,  8, 12, 19],
  [3,   6,  9, 16, 22],
  [10, 13, 14, 17, 24],
  [18, 21, 23, 26, 30]
]
```

 给定 target = `5`，返回 `true`。 

给定 target = `20`，返回 `false`。

**思路和代码：**

我们分析该二维数组的特点，左到右递增，上到下递增，因此可以从右上角开始寻找。

如果比目标值大，就往左边找，如果比目标值小，就往下边找。

```java
class Solution {
    public boolean findNumberIn2DArray(int[] matrix, int target) {
        if(matrix.length==0||matrix[0].length==0)
            return false;
        int row = 0;		//起始行为第一行
        int col = matrix[0].length-1; 	//起始列为最后一列
        while(row < matrix.length && col >= 0) { 	//边界条件
            if(matrix[row][col] > target) 
                col--;
            else if(matrix[row][col] < target)
                row++;
            else
                return true;
        }
        return false;
    }
}
```





#### [面试题05. 替换空格](https://leetcode-cn.com/problems/ti-huan-kong-ge-lcof/)

 请实现一个函数，把字符串 `s` 中的每个空格替换成"%20"。 

 **示例 1：** 

```java
输入：s = "We are happy."
输出："We%20are%20happy."
```

**思路和代码：**

这道题很简单没什么好说的，利用StringBuilder拼接字符串即可，如果遇到空格就替换。

```java
class Solution {
    public String replaceSpace(String s) {
        int n = s.length();
        StringBuilder res = new StringBuilder();
        for(int i=0; i<n; i++) {
            if(s.charAt(i) == ' ')
                res.append("%20");
            else
                res.append(s.charAt(i));
        }
        return res.toString();
    }
}
```





#### [面试题06. 从尾到头打印链表](https://leetcode-cn.com/problems/cong-wei-dao-tou-da-yin-lian-biao-lcof/)

输入一个链表的头节点，从尾到头反过来返回每个节点的值（用数组返回）。

**示例 1：**

```java
`输入：head = [``1``,``3``,``2``]``输出：[``2``,``3``,``1``]`
```

**思路和代码：**

方法一：利用LinkedList顺序保存链表，然后逆序保存到结果数组中返回即可。

```java
class Solution {
    public int[] reversePrint(ListNode head) {
        LinkedList<Integer> stack = new LinkedList<>();
        while(head != null) {
            stack.addLast(head.val);
            head = head.next;
        }
        int[] res = new int[stack.size()];
        for(int i=0; i<res.length; i++) {
            res[i] = stack.removeLast();
        }
        return res;
    }
}
```

方法二：递归至尾节点后逐步输出

```java
class Solution {
    ArrayList<Integer> tmp = new ArrayList<>();
    public int[] reversePrint(ListNode head) {
        reverse(head);
        int[] res = new int[tmp.size()];
        for(int i=0; i<tmp.size(); i++) {
            res[i] = tmp.get(i);
        }
        return res;
    }
    void reverse(ListNode head) {
        if(head == null) return;
        reverse(head.next);
        tmp.add(head.val);
    }
}
```





#### [面试题07. 重建二叉树](https://leetcode-cn.com/problems/zhong-jian-er-cha-shu-lcof/)

输入某二叉树的前序遍历和中序遍历的结果，请重建该二叉树。假设输入的前序遍历和中序遍历的结果中都不含重复的数字。

例如，给出

```java
`前序遍历 preorder = [``3``,``9``,``20``,``15``,``7``]``中序遍历 inorder = [``9``,``3``,``15``,``20``,``7``]`
```

返回如下的二叉树：

```java
    3
   / \
  9  20
    /  \
   15   7
```

 **思路和代码：** 

```java
class Solution {
    //key是中序遍历的值，value是中序遍历的结果
    HashMap<Integer,Integer> indexMap=new HashMap<>();

    public TreeNode buildTree(int[] preorder, int[] inorder) {
        //保存中序遍历的信息
        for(int i=0;i<inorder.length;i++){
            indexMap.put(inorder[i],i);
        }
        return createTree(preorder,0,inorder,0,inorder.length-1);
    }

    //preIndex是前序遍历的索引，inStart和inEnd是中序遍历的索引范围
    private TreeNode createTree(int[] preorder,int preIndex,int[] inorder,int inStart,int inEnd){
        if(inStart>inEnd)
            return null;
        //获取前序遍历的值
        int val=preorder[preIndex];
        //获取前序遍历值在中序遍历的位置
        int inIndex=indexMap.get(val);
        //以该值作为根节点的值创建根节点
        TreeNode root=new TreeNode(val);
        //根节点的左子树节点数目
        int leftNum=inIndex-inStart;
        //根节点以左创建左子树，根节点以右创建右子树
        root.left=createTree(preorder,preIndex+1,inorder,inStart,inIndex-1);
        root.right=createTree(preorder,preIndex+1+leftNum,inorder,inIndex+1,inEnd);
        return root;
    }
}
```





#### [面试题09. 用两个栈实现队列](https://leetcode-cn.com/problems/yong-liang-ge-zhan-shi-xian-dui-lie-lcof/)

用两个栈实现一个队列。队列的声明如下，请实现它的两个函数 `appendTail` 和 `deleteHead` ，分别完成在队列尾部插入整数和在队列头部删除整数的功能。(若队列中没有元素，`deleteHead` 操作返回 -1 )

**示例 1：**

```java
输入：
["CQueue","appendTail","deleteHead","deleteHead"]
[[],[3],[],[]]
输出：[null,null,3,-1]
```

 **示例 2：** 

```java
输入：
["CQueue","deleteHead","appendTail","appendTail","deleteHead","deleteHead"]
[[],[],[5],[2],[],[]]
输出：[null,-1,null,null,5,2]
```

 **思路和代码：** 

```java
class CQueue {
    //不推荐使用Stack的方式来做这道题，会造成速度较慢； 原因的话是Stack继承了Vector接口，而Vector底层是一个Object[]数组（官方已不推荐使用Stack），那么就要考虑空间扩容和移位的问题了。 可以使用LinkedList来做Stack的容器，因为LinkedList实现了Deque接口，所以Stack能做的事LinkedList都能做，其本身结构是个双向链表，扩容消耗少。
    LinkedList<Integer> A,B;
    public CQueue() {
        A = new LinkedList<Integer>();
        B = new LinkedList<Integer>();
    }
    
    public void appendTail(int value) {
        A.addLast(value);
    }
    
    public int deleteHead() {
        if(!B.isEmpty()) return B.removeFirst();
        if(A.isEmpty()) return -1;
        while(!A.isEmpty()) {
            B.addLast(A.removeFirst());
        }
        return B.removeFirst();
    }
}
```





#### [面试题10- I. 斐波那契数列](https://leetcode-cn.com/problems/fei-bo-na-qi-shu-lie-lcof/)

写一个函数，输入 `n` ，求斐波那契（Fibonacci）数列的第 `n` 项。斐波那契数列的定义如下：

```java
F(0) = 0,   F(1) = 1
F(N) = F(N - 1) + F(N - 2), 其中 N > 1.
```

斐波那契数列由 0 和 1 开始，之后的斐波那契数就是由之前的两数相加而得出。

答案需要取模 1e9+7（1000000007），如计算初始结果为：1000000008，请返回 1。

**示例 1：**

```java
`输入：n = ``2``输出：``1`
```

**示例 2：**

```java
输入：n = 5
输出：5
```

 **思路和代码：** 

简单的动态规划

```java
class Solution {
    public int numWays(int n) {
        int a = 1, b = 1, sum;
        for(int i = 0; i < n; i++){
            sum = (a + b) % 1000000007;
            a = b;
            b = sum;
        }
        return a;
    }
}
```





#### [面试题10- II. 青蛙跳台阶问题](https://leetcode-cn.com/problems/qing-wa-tiao-tai-jie-wen-ti-lcof/)

一只青蛙一次可以跳上1级台阶，也可以跳上2级台阶。求该青蛙跳上一个 `n` 级的台阶总共有多少种跳法。

 答案需要取模 1e9+7（1000000007），如计算初始结果为：1000000008，请返回 1。 

**示例 1：**

```java
`输入：n = ``2``输出：``2`
```

 **示例 2：** 

```java
输入：n = 7
输出：21
```

**提示：**

- `0 <= n <= 100`

**思路和代码：**

简单的动态规划，跳到0或1级有1种方法，之后跳到i的方法数量=跳到i-1的方法数量+跳到i-2的方法数量（因为每次可以跳1或2级）。

由于每次结果要取模所以要mod1000000007。

方法一、空间复杂度O(n)

```java
class Solution {
    public int numWays(int n) {
        if(n < 2) return 1;
        int[] dp = new int[n+1];
        dp[0] = 1; 
        dp[1] = 1; 
        for(int i = 2; i <= n; i++){
            dp[i] = (dp[i-1]+dp[i-2]) % 1000000007;
        }
        return dp[n];
    }
}
```

方法二、优化为O(1)空间复杂度

```java
class Solution {
    public int numWays(int n) {
        int a = 1, b = 1, sum;
        for(int i = 0; i < n; i++){
            sum = (a + b) % 1000000007;
            a = b;
            b = sum;
        }
        return a;
    }
}
```





#### [面试题11. 旋转数组的最小数字](https://leetcode-cn.com/problems/xuan-zhuan-shu-zu-de-zui-xiao-shu-zi-lcof/)

把一个数组最开始的若干个元素搬到数组的末尾，我们称之为数组的旋转。输入一个递增排序的数组的一 个旋转，输出旋转数组的最小元素。例如，数组 `[3,4,5,1,2]` 为 `[1,2,3,4,5]` 的一个旋转，该数组的最小值为1。 

 **示例 1：** 

```java
输入：[3,4,5,1,2]
输出：1
```

 **示例 2：** 

```java
输入：[2,2,2,0,1]
输出：0
```

**思路和代码：**

方法一、从头遍历，如果一个数字大于它的下一个，就返回它的下一个。

例如示例1，5>1，返回1，示例2，2>0，返回0。

如果没找到就返回第一个，例如12345返回1。

```java
class Solution {
    public int minArray(int[] numbers) {
        for(int i=0;i<numbers.length-1;i++){
            if(numbers[i]>numbers[i+1])
                return numbers[i+1];
        }
        return numbers[0];
    }
}
```

方法二、优化为二分查找

```java
class Solution {
public int minArray(int[] numbers) {
        int start = 0;
        int end = numbers.length - 1;
        while(start != end){
            int mid = start + (end - start) / 2;
            if(numbers[mid] > numbers[end]) start = mid + 1;
            else if(numbers[mid] < numbers[end]) end = mid;
            else return findMin(numbers,start,end);
        }
        return numbers[start];
    }

    public int findMin(int[] numbers,int start,int end){
        int result = numbers[start];
        for(int i = start;i <= end;i++){
            if (numbers[i] < result) result = numbers[i];
        }
        return result;
    }
}
```





#### [面试题12. 矩阵中的路径](https://leetcode-cn.com/problems/ju-zhen-zhong-de-lu-jing-lcof/)

请设计一个函数，用来判断在一个矩阵中是否存在一条包含某字符串所有字符的路径。路径可以从矩阵中的任意一格开始，每一步可以在矩阵中向左、右、上、下移动一格。如果一条路径经过了矩阵的某一格，那么该路径不能再次进入该格子。例如，在下面的3×4的矩阵中包含一条字符串“bfce”的路径（路径中的字母用加粗标出）。 

 [["a","**b**","c","e"],
["s","**f**","**c**","s"],
["a","d","**e**","e"]] 

 但矩阵中不包含字符串“abfb”的路径，因为字符串的第一个字符b占据了矩阵中的第一行第二个格子之后，路径不能再次进入这个格子。 

 **示例 1：** 

```java
输入：board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"
输出：true
```

 **示例 2：** 

```java
输入：board = [["a","b"],["c","d"]], word = "abcd"
输出：false
```

**思路和代码：**

使用深度优先搜索回溯，从全部字符以头开始遍历，如果寻找到了就直接返回true，否则继续以下一个字符为头重新开始。

k代表已经成功匹配的字符数量，初始为0，每匹配一个加1，当达到目标长度时返回true。

每次进行下一层搜索时将当前字符设为一个非字母值，这样可以防止重复遍历。

```java
class Solution {
    public boolean exist(char[][] board, String word) {
        char[] words=word.toCharArray();
        for(int i=0;i<board.length;i++){
            for(int j=0;j<board[0].length;j++){
                if(dfs(board,words,i,j,0))
                    return true;
            }
        }
        return false;
    }

    private boolean dfs(char[][] board,char[] words,int i,int j,int k){
        if(i<0||j<0||i==board.length||j==board[0].length)//边界判断防止越界
            return false;
        if(board[i][j]!=words[k])//如果遍历字符和目标字符不符，返回false
            return false;
        //如果全部匹配成功，k已达到目标数组长度，返回true
        if(k==words.length-1)
            return true;
        char temp=board[i][j];//保存当前字符
        board[i][j]='/';//当前字符遍历后，防止在dfs中重复遍历，设为任意非字母字符
        //保存当前结果
        boolean res=dfs(board,words,i+1,j,k+1)
            ||dfs(board,words,i-1,j,k+1)
            ||dfs(board,words,i,j+1,k+1)
            ||dfs(board,words,i,j-1,k+1);
        board[i][j]=temp;//还原字符，下次遍历正常
        //还原字符后返回结果
        return res;
    }
}
```





#### [面试题13. 机器人的运动范围](https://leetcode-cn.com/problems/ji-qi-ren-de-yun-dong-fan-wei-lcof/)

地上有一个m行n列的方格，从坐标 `[0,0]` 到坐标 `[m-1,n-1]` 。一个机器人从坐标 `[0, 0]`的格子开始移动，它每次可以向左、右、上、下移动一格（不能移动到方格外），也不能进入行坐标和列坐标的数位之和大于k的格子。例如，当k为18时，机器人能够进入方格 [35, 37] ，因为3+5+3+7=18。但它不能进入方格 [35, 38]，因为3+5+3+8=19。请问该机器人能够到达多少个格子？ 

 **示例 1：** 

```java
输入：m = 2, n = 3, k = 1
输出：3
```

 **示例 2：** 

```java
输入：m = 3, n = 1, k = 0
输出：1
```

**提示：**

- `1 <= n,m <= 100`
- `0 <= k <= 20`

**思路和代码：**

由于最多100行，100列，因此索引从0~99。用/和%计算各位的数字之和，例如35和37，35/10+35%10+37/10+37%10=18。

一、DFS

```java
class Solution {
    boolean[][] visited;
    public int movingCount(int m, int n, int k) {
        visited = new boolean[m][n];
        return dfs(0,0,m,n,k);
    }

    private int dfs(int i, int j, int m, int n, int k) {
        if(i>=m || j>=n || visited[i][j] || (i%10 + i/10 + j%10 + j/10)>k)
            return 0;
        visited[i][j] = true;
        return dfs(i+1, j, m, n, k) + dfs(i, j+1, m, n, k) + 1;
    }
}
```

二、BFS

```java
class Solution {
    public int movingCount(int m, int n, int k) {
    boolean[][] visited = new boolean[m][n];
    int res = 0;
    //创建一个队列，保存的是访问到的格子坐标，是个二维数组
    Queue<int[]> queue = new LinkedList<>();
    //从左上角坐标[0,0]点开始访问，add方法表示把坐标点加入到队列的队尾
    queue.add(new int[]{0, 0});
    while (queue.size() > 0) {
        int[] x = queue.poll();
        int i = x[0], j = x[1];
        if (i >= m || j >= n || (i%10 + i/10 + j%10 + j/10)>k|| visited[i][j])
            continue;
        visited[i][j] = true;
        res++;
        //把当前格子右边格子的坐标加入到队列中
        queue.add(new int[]{i + 1, j});
        //把当前格子下边格子的坐标加入到队列中
        queue.add(new int[]{i, j + 1});
    }
    return res;
}
```





#### [面试题14- I. 剪绳子](https://leetcode-cn.com/problems/jian-sheng-zi-lcof/)

 给你一根长度为 `n` 的绳子 ，请把绳子剪成整数长度的 `m` 段（m、n都是整数，n>1并且m>1），每段绳子的长度记为 `k[0],k[1]...k[m]` 。请问 `k[0]*k[1]*...*k[m]` 可能的最大乘积是多少？例如，当绳子的长度是8时，我们把它剪成长度分别为2、3、3的三段，此时得到的最大乘积是18。 

 **示例 1：**

```java
输入: 2
输出: 1
解释: 2 = 1 + 1, 1 × 1 = 1
```

 **示例 2:** 

```java
输入: 10
输出: 36
解释: 10 = 3 + 3 + 4, 3 × 3 × 4 = 36
```

**提示：**

- `2 <= n <= 58`

**思路和代码：**

 **推论一：** 将绳子 **以相等的长度等分为多段** ，得到的乘积最大。 

 **推论二：** 尽可能将绳子以长度 3 等分为多段时，乘积最大。 

```java
class Solution {
    public int cuttingRope(int n) {
        if(n < 4) return n - 1;
        int cnt = 1;
        while(n > 4) {
            cnt *= 3;
            n -= 3;
        }
        return n*cnt;
    }
}
```

或者分三种情况直接求积

切分规则：
最优： 3 。把绳子尽可能切为多个长度为 3 的片段，留下的最后一段绳子的长度可能为 0,1,2三种情况。
次优： 2 。若最后一段绳子长度为 2 ；则保留，不再拆为 1+1 。
最差： 1 。若最后一段绳子长度为 1 ；则应把一份 3+1 替换为 2+2，因为 2×2 > 3×1。

```java
class Solution {
    public int cuttingRope(int n) {
        if(n <= 3) return n - 1;
        int a = n/3, b = n%3;
        if(b == 0) 	//情况1，是3的倍数
            return (int)Math.pow(3, a);
        if(b == 1) 	//情况2，余1，拆出一个4
            return (int)Math.pow(3, a - 1) * 4;
        return (int)Math.pow(3, a) * 2;	//情况3，余2，拆出一个2
    }
}
```





#### [面试题14- II. 剪绳子 II](https://leetcode-cn.com/problems/jian-sheng-zi-ii-lcof/)

 给你一根长度为 `n` 的绳子 ，请把绳子剪成整数长度的 `m` 段（m、n都是整数，n>1并且m>1），每段绳子的长度记为 `k[0],k[1]...k[m]` 。请问 `k[0]*k[1]*...*k[m]` 可能的最大乘积是多少？例如，当绳子的长度是8时，我们把它剪成长度分别为2、3、3的三段，此时得到的最大乘积是18。 

 答案需要取模 1e9+7（1000000007），如计算初始结果为：1000000008，请返回 1。 

 **思路和代码：** 

同上一题，取个模就行

```java
class Solution {
    public int cuttingRope(int n) {
        long res = 1;
        if(n < 4)
            return n-1;
        while(n > 4) {
            res *= 3;
            res %= 1000000007;
            n -= 3;
        }
        return (int) (n*res%1000000007);
    }
}
```





#### [面试题15. 二进制中1的个数](https://leetcode-cn.com/problems/er-jin-zhi-zhong-1de-ge-shu-lcof/)

 请实现一个函数，输入一个整数，输出该数二进制表示中 1 的个数。例如，把 9 表示成二进制是 1001，有 2 位是 1。因此，如果输入 9，则该函数输出 2。 

 **示例 1：** 

```java
输入：00000000000000000000000000001011
输出：3
解释：输入的二进制串 00000000000000000000000000001011 有三位为 '1'。
```

 **示例 2：** 

```java
输入：00000000000000000000000010000000
输出：1
解释：输入的二进制串 00000000000000000000000010000000 有一位为 '1'。
```

 **思路和代码：** 

方法一、根据与运算特点，使n与1逐位比较，判断n最右一位是否为1，根据结果计数

```java
public class Solution {
    // >>>为无符号数右移
    public int hammingWeight(int n) {
        int res = 0;
        while (n != 0) {
            res += n & 1;
            n >>>= 1;
        }
        return res;
    }
}
```

方法二、利用n&(n-1)

- (n−1) ： 二进制数字 n 最右边的 1 变成 0 ，此 1 右边的 0 都变成 1 。
- n&(n−1) ： 二进制数字 n 最右边的 1 变成 0 ，其余不变。

```java
public class Solution {
    public int hammingWeight(int n) {
        int res = 0;
        while(n != 0) {
            res++;
            n &= n - 1;
        }
        return res;
    }
}
```





#### [面试题16. 数值的整数次方](https://leetcode-cn.com/problems/shu-zhi-de-zheng-shu-ci-fang-lcof/)

 实现函数double Power(double base, int exponent)，求base的exponent次方。不得使用库函数，同时不需要考虑大数问题。 

 **示例 1:** 

```java
输入: 2.00000, 10
输出: 1024.00000
```

 **示例 2:** 

```java
输入: 2.10000, 3
输出: 9.26100
```

 **示例 3:** 

```java
输入: 2.00000, -2
输出: 0.25000
解释: 2-2 = 1/22 = 1/4 = 0.25
```

 **思路和代码：** 

快速幂法，注意区分奇偶即可

```java
class Solution {
    public double myPow(double x, int n) {
        double res = 1.0;
        for(int i=n; i!=0; i/=2) {
            if(i%2 != 0)
                res *= x;
            x *= x;
        }
        return n > 0 ? res : 1/res;
    }
}
```





#### [面试题17. 打印从1到最大的n位数](https://leetcode-cn.com/problems/da-yin-cong-1dao-zui-da-de-nwei-shu-lcof/)

输入数字 `n`，按顺序打印出从 1 到最大的 n 位十进制数。比如输入 3，则打印出 1、2、3 一直到最大的 3 位数 999。

**示例 1:**

```java
输入: n = 1
输出: [1,2,3,4,5,6,7,8,9]
```

说明：

- 用返回一个整数列表来代替打印
- n 为正整数

 **思路和代码：** 

本意是考察大数问题，不考虑大数解法：

```java
class Solution {
    public int[] printNumbers(int n) {
        int end = (int)Math.pow(10, n) - 1;
        int[] res = new int[end];
        for(int i = 0; i < end; i++)
            res[i] = i + 1;
        return res;
    }
}
```

大数问题解法：

```java
public class solution {
    public void printNumbers(int n) {
        StringBuilder str = new StringBuilder();
        // 将str初始化为n个'0'字符组成的字符串
        for (int i = 0; i < n; i++) {
            str.append('0');
        }
        while(!increment(str)){
            // 去掉左侧的0
            int index = 0;
            while (index < str.length() && str.charAt(index) == '0'){
                index++;
            }
            System.out.println(str.toString().substring(index));
        }
    }

    public boolean increment(StringBuilder str) {
        boolean isOverflow = false;
        for (int i = str.length() - 1; i >= 0; i--) {
            char s = (char)(str.charAt(i) + 1);
            // 如果s大于'9'则发生进位
            if (s > '9') {
                str.replace(i, i + 1, "0");
                if (i == 0) {
                    isOverflow = true;
                }
            }
            // 没发生进位则跳出for循环
            else {
                str.replace(i, i + 1, String.valueOf(s));
                break;
            }
        }
        return isOverflow;
    }
}
```





#### [面试题18. 删除链表的节点](https://leetcode-cn.com/problems/shan-chu-lian-biao-de-jie-dian-lcof/)

给定单向链表的头指针和一个要删除的节点的值，定义一个函数删除该节点。

返回删除后的链表的头节点。

 **示例 1:** 

```java
输入: head = [4,5,1,9], val = 5
输出: [4,1,9]
解释: 给定你链表中值为 5 的第二个节点，那么在调用了你的函数之后，该链表应变为 4 -> 1 -> 9.
```

 **示例 2:** 

```java
输入: head = [4,5,1,9], val = 1
输出: [4,5,9]
解释: 给定你链表中值为 1 的第三个节点，那么在调用了你的函数之后，该链表应变为 4 -> 5 -> 9.
```

 **思路和代码：** 

```java
class Solution {
    public ListNode deleteNode(ListNode head, int val) {
        ListNode pre = head, cur = head.next;
        if(head.val == val) return head.next;
        while(cur.val != val && cur != null) {
            pre = pre.next;
            cur = cur.next;
        }
        if(cur != null) {
            pre.next = cur.next;
        }
        return head;
    }
}
```





#### [面试题19. 正则表达式匹配](https://leetcode-cn.com/problems/zheng-ze-biao-da-shi-pi-pei-lcof/)

请实现一个函数用来匹配包含`'. '`和`'*'`的正则表达式。模式中的字符`'.'`表示任意一个字符，而`'*'`表示它前面的字符可以出现任意次（含0次）。 在本题中，匹配是指字符串的所有字符匹配整个模式。例如，字符串`"aaa"`与模式`"a.a"`和`"ab*ac*a"`匹配，但与`"aa.a"`和`"ab*a"`均不匹配。 

 **示例 1:** 

```java
输入:
s = "aa"
p = "a"
输出: false
解释: "a" 无法匹配 "aa" 整个字符串。
```

 **示例 2:** 

```java
输入:
s = "aa"
p = "a*"
输出: true
解释: 因为 '*' 代表可以匹配零个或多个前面的那一个元素, 在这里前面的元素就是 'a'。因此，字符串 "aa" 可被视为 'a' 重复了一次。

```

 **示例 3:** 

```java
输入:
s = "ab"
p = ".*"
输出: true
解释: ".*" 表示可匹配零个或多个（'*'）任意字符（'.'）。
```

 **示例 4:** 

```java
输入:
s = "mississippi"
p = "mis*is*p*."
输出: false
```

 **思路和代码：** 

```java
class Solution {
    public boolean isMatch(String s, String p) {
        //任意一个为空，则匹配失败
        if(s==null||p==null)
            return false;
        return match(s.toCharArray(),0,p.toCharArray(),0);
    }

    public boolean match(char[] str, int s,char[] pattern,int p){
        //如果字符串和匹配字符串都到达了末尾，则说明匹配成功
        if(s==str.length&&p==pattern.length)
            return true;
        //如果字符串未遍历结束，但匹配字符串已结束，匹配失败
        if(s<str.length&&p==pattern.length)
            return false;
        //如果匹配字符串的下一个字符是*
        if(p<pattern.length-1&&pattern[p+1]=='*'){
            //如果当前字符串字符和匹配字符串字符相同或者匹配字符为.
            if(s<str.length&&(str[s]==pattern[p]||pattern[p]=='.'))
                return match(str, s+1, pattern, p)//.*可以匹配多个字符 如aa匹配a*
                     ||match(str, s, pattern, p+2);//字符串已匹配完，放弃匹配字符串的两个位置，例如a匹配ab*
            else
                return match(str, s, pattern, p+2);//忽略当前匹配字符串的2个字符 如a不匹配b*，可跳过b*这两个位置
        }
        //匹配字符串没有下一个位置或下一个位置不为*，那么当前位置必须相等或为.，否则匹配失败
        if(s<str.length&&(str[s]==pattern[p]||pattern[p]=='.')){
            return match(str,s+1,pattern,p+1);//各自匹配一个位置
        }
        return false;
    }
}
```





#### [面试题20. 表示数值的字符串](https://leetcode-cn.com/problems/biao-shi-shu-zhi-de-zi-fu-chuan-lcof/)

请实现一个函数用来判断字符串是否表示数值（包括整数和小数）。例如，字符串"+100"、"5e2"、"-123"、"3.1416"、"0123"都表示数值，但"12e"、"1a3.14"、"1.2.3"、"+-5"、"-1E-16"及"12e+5.4"都不是。 

 **思路和代码：** 

[abc]表示匹配a、b、c任意一个即可。[0-9]表示匹配数字0-9

`\\.`表示小数点，？表示0或1次，+表示1或多次，*表示任意次，|表示或。

首先判断开头，[+-]？表示可以以加号或减号开头，也可以不以加减号开头。

数字部分是`[0-9]+\\.?`表示0-9必须出现一次，小数点可以不出现，例如`111`，`11.`

 或者是`[0-9]*\\.[0-9]+`，表示小数点前任意次，小数点必须有，小数点后必须有，例如`.5`，`1.5` 

 最后指数`[e][+-]?[0-9]+`匹配时表示必须有e，正负号可有可无，有e时后面必须有数字，？表示也可以没指数。 

```java
class Solution {
    public boolean isNumber(String s) {
        return s.trim()
                .matches("^[+-]?(([0-9]+\\.?)|([0-9]*\\.[0-9]+))([e][+-]?[0-9]+)?$");
    }
}

```





#### [面试题21. 调整数组顺序使奇数位于偶数前面](https://leetcode-cn.com/problems/diao-zheng-shu-zu-shun-xu-shi-qi-shu-wei-yu-ou-shu-qian-mian-lcof/)

 输入一个整数数组，实现一个函数来调整该数组中数字的顺序，使得所有奇数位于数组的前半部分，所有偶数位于数组的后半部分。 

 **示例：** 

```java
输入：nums = [1,2,3,4]
输出：[1,3,2,4] 
注：[3,1,2,4] 也是正确的答案之一。

```

**思路与代码：**

 类似于快速排序的思想，使用双指针，从头找偶数，从尾找奇数，然后交换它们的位置。 

```java
class Solution {

    public int[] exchange(int[] nums) {
        int p = 0;
        int q = nums.length-1;
        while(p < q){
            //从前面找到第一个偶数
            while(p <= q && nums[p]%2 != 0)
                p++;
            //从后面找到第一个奇数
            while(p <= q && nums[q]%2 == 0)
                q--;
            if(p < q){//交换数字
                int temp=nums[p];
                nums[p]=nums[q];
                nums[q]=temp;
            }
        }
        return nums;
    }
}

```





#### [面试题22. 链表中倒数第k个节点](https://leetcode-cn.com/problems/lian-biao-zhong-dao-shu-di-kge-jie-dian-lcof/)

输入一个链表，输出该链表中倒数第k个节点。为了符合大多数人的习惯，本题从1开始计数，即链表的尾节点是倒数第1个节点。例如，一个链表有6个节点，从头节点开始，它们的值依次是1、2、3、4、5、6。这个链表的倒数第3个节点是值为4的节点。 

**示例：**

```java
给定一个链表: 1->2->3->4->5, 和 k = 2.
返回链表 4->5.

```

 **思路和代码：** 

 使用双指针，让前指针先走k个，这样当前指针为null时后指针就是答案。 

```java
class Solution {
    public ListNode getKthFromEnd(ListNode head, int k) {
        ListNode pre = head, cur = head;
        for(int i=0; i<k; i++)
            cur = cur.next;
        while(cur != null) {
            pre = pre.next;
            cur = cur.next;
        }
        return pre;
    }
}
```





#### [面试题24. 反转链表](https://leetcode-cn.com/problems/fan-zhuan-lian-biao-lcof/)

定义一个函数，输入一个链表的头节点，反转该链表并输出反转后链表的头节点。

 **示例:** 

```java
输入: 1->2->3->4->5->NULL
输出: 5->4->3->2->1->NULL
```

**思路和代码：**

方法一、利用两个指针，pre指针保存前一个节点，cur指针用于遍历链表， 每次迭代到 cur，都将 cur 的 next 指向 pre，然后 pre 和 cur 前进一位。 

![img](https://pic.leetcode-cn.com/fd2b1e4fe949ed0c09991c529e780708b2c68dc3d018342d51b846268369c3ef.gif)

```java
class Solution {
    public ListNode reverseList(ListNode head) {
        ListNode pre, cur;
        pre = null;
        while(head != null) {
            cur = head.next;
            head.next = pre;
            pre = head;
            head = cur;
        }
        return pre;
    }
}

```

方法二、递归

![img](https://pic.leetcode-cn.com/5ff86a743320333d3fe335c711182de37fb0fce958a005064254b4b48b2958a9.gif)

```java
class Solution {
    public ListNode reverseList(ListNode head) {
        //递归终止条件是当前为空，或下一节点为空
        if(head == null || head.next == null)
            return head;
        ListNode cur = reverseList(head.next);
        //反转节点
        head.next.next = head;
        //防止列表循环，需将head.next置空
        head.next = null;
        //每层递归都返回cur，即最后一个节点
        return cur;
    }
}

```





#### [面试题25. 合并两个排序的链表](https://leetcode-cn.com/problems/he-bing-liang-ge-pai-xu-de-lian-biao-lcof/)

输入两个递增排序的链表，合并这两个链表并使新链表中的节点仍然是递增排序的。

 **示例1：** 

```java
输入：1->2->4, 1->3->4
输出：1->1->2->3->4->4

```

**思路和代码：**

比较简单，由于是有序链表，所以分别从头开始遍历，如果l1更小，将节点的下一个指向l1，否则就指向l2。如果有一个为空，就将另一个剩下的链表直接拼接。

```java
class Solution {

    public ListNode mergeTwoLists(ListNode l1, ListNode l2) {
        ListNode pre = new ListNode(-1);
        ListNode cur = pre;
        while(l1!=null && l2!=null) {
            if(l1.val < l2.val){
                cur.next = l1;
                l1 = l1.next;
            } else {
                cur.next = l2;
                l2 = l2.next;
            }
            cur = cur.next;
        }
        cur.next = l1==null ? l2:l1;
        return pre.next;
    }
}

```





#### [面试题26. 树的子结构](https://leetcode-cn.com/problems/shu-de-zi-jie-gou-lcof/)

输入两棵二叉树A和B，判断B是不是A的子结构。(约定空树不是任意一个树的子结构)

B是A的子结构， 即 A中有出现和B相同的结构和节点值。 

 **示例 1：** 

```java
输入：A = [1,2,3], B = [3,1]
输出：false

```

 **示例 2：** 

```java
输入：A = [3,4,5,1,2], B = [4,1]
输出：true

```

**思路和代码**

递归即可

```java
class Solution {
    public boolean isSubStructure(TreeNode A, TreeNode B) {
        if(A == null || B == null)
            return false;
        return dfs(A,B) || isSubStructure(A.left,B) || isSubStructure(A.right,B);
    }

    private boolean dfs(TreeNode A, TreeNode B) {
        if(B == null) return true;
        if(A == null) return false;
        return A.val == B.val && dfs(A.right,B.right) && dfs(A.left ,B.left);
    }
}

```





#### [面试题27. 二叉树的镜像](https://leetcode-cn.com/problems/er-cha-shu-de-jing-xiang-lcof/)

请完成一个函数，输入一个二叉树，该函数输出它的镜像。

 **示例 ：** 

```java
输入：  4
    /    \
   2      7
  /  \    / \
  1   3  6   9
    
输出：  4
     /   \
    7      2
   / \    / \
  9   6  3   1

```

**思路和代码**

方法一、简单递归

```java
class Solution {
    public TreeNode mirrorTree(TreeNode root) {
        if(root!=null) {
            //将右子树翻转作为新的左子树
            TreeNode newLeft = mirrorTree(root.right);
            //将左子树翻转作为新的右子树
            TreeNode newRight = mirrorTree(root.left);
            root.left = newLeft;
            root.right = newRight;
        }
        return root;
    }
}
```

方法二、借助辅助栈或队列

```java
class Solution {
    public TreeNode mirrorTree(TreeNode root) {
        if(root == null) return null;
        Stack<TreeNode> stack = new Stack<>();
        stack.push(root);
        while(!stack.isEmpty()) {
            TreeNode node = stack.pop();
            if(node.left != null) stack.push(node.left);
            if(node.right != null) stack.push(node.right);
            TreeNode temp = node.left;
            node.left = node.right;
            node.right = temp;
        }
        return root;
    }
}
```





#### [面试题28. 对称的二叉树](https://leetcode-cn.com/problems/dui-cheng-de-er-cha-shu-lcof/)

给定一个二叉树，检查它是否是镜像对称的。

 例如，二叉树 `[1,2,2,3,4,4,3]` 是对称的。 

```java
    1
   / \
  2   2
 / \ / \
3  4 4  3

```

 但是下面这个 `[1,2,2,null,3,null,3]` 则不是镜像对称的: 

```java
    1
   / \
  2   2
   \   \
   3    3

```

 **思路和代码：**

 如果根节点为空，那么空节点是对称的，否则比较它的左右子树是否对称。

如果都为空那对称，如果只有一个为空肯定不对称。

如果都不为空那么比较值，值不同肯定不对称，如果值相同，再比较左节点的右子树和右节点的左子树是否对称（最里面那一层），比较左节点的左子树和右节点的右子树是否对称（最外面那一层）。

```java
class Solution {
    public boolean isSymmetric(TreeNode root) {
        if(root == null) return true;
        return helper(root.left,root.right);
    }

    private boolean helper(TreeNode root1, TreeNode root2) {
        if(root1 == null && root2 == null) return true;
        if(root1 == null || root2 == null) return false;
        return root1.val == root2.val && helper(root1.left,root2.right) && helper(root1.right,root2.left);
    }
}

```





#### [面试题29. 顺时针打印矩阵](https://leetcode-cn.com/problems/shun-shi-zhen-da-yin-ju-zhen-lcof/)

输入一个矩阵，按照从外向里以顺时针的顺序依次打印出每一个数字。

**示例 1：**

```java
输入：matrix = [[1,2,3],[4,5,6],[7,8,9]]
输出：[1,2,3,6,9,8,7,4,5]

```

 **示例 2：** 

```java
输入：matrix = [[1,2,3,4],[5,6,7,8],[9,10,11,12]]
输出：[1,2,3,4,8,12,11,10,9,5,6,7]

```

**限制：**

- `0 <= matrix.length <= 100`
- `0 <= matrix[i].length <= 100`

**思路和代码：**

在循环中按照右下左上的顺序循环，每次改变方向前先判断是否越界。

```java
class Solution {
    public int[] spiralOrder(int[][] matrix) {
        if(matrix.length == 0) return new int[0];
        int[] res = new int[matrix.length*matrix[0].length]; 
        int left=0, right=matrix[0].length-1, top=0, bottom=matrix.length-1, r=0;
        while(true) {
            //从左向右移动
            for(int i=left; i<=right; i++) 
                res[r++] = matrix[top][i];
            if(++top > bottom) break;
            //从上向下移动
            for(int i=top; i<=bottom; i++) 
                res[r++] = matrix[i][right];
            if(--right < left) break;
            //从右向左移动
            for(int i=right; i>=left; i--) 
                res[r++] = matrix[bottom][i];
            if(--bottom < top) break;
             //从下向上移动
            for(int i=bottom; i>=top; i--) 
                res[r++] = matrix[i][left];
            if(++left > right) break;
        }
        return res;
    }
}

```





#### [面试题30. 包含min函数的栈](https://leetcode-cn.com/problems/bao-han-minhan-shu-de-zhan-lcof/)

定义栈的数据结构，请在该类型中 实现一个能够得到栈的最小元素的 min 函数在该栈中，调用 min、push 及 pop 的时间复杂度都是 O(1)。 

 **示例:** 

```java
MinStack minStack = new MinStack();
minStack.push(-2);
minStack.push(0);
minStack.push(-3);
minStack.min();   --> 返回 -3.
minStack.pop();
minStack.top();      --> 返回 0.
minStack.min();   --> 返回 -2.
```

 **思路和代码：** 

 使用一个辅助栈helper作为最小栈，进栈出栈helper都没有限制，对于最小栈helper只有helper为空或入栈节点值小于等于helper栈顶时才可入栈，出栈时，只有data和helper栈顶相同helper才出栈。 

```java
class MinStack {
    private Stack<Integer> data;
    private Stack<Integer> helper;
    /** initialize your data structure here. */
    public MinStack() {
        data = new Stack<>();
        helper = new Stack<>();
    }
    
    public void push(int x) {
        data.push(x);
        if(helper.isEmpty() || helper.peek() >= x) 
            helper.push(x);
    }
    
    public void pop() {
        //data栈比较时即弹出
        if(helper.peek().equals(data.pop()))
            helper.pop();
    }
    
    public int top() {
        return data.peek();
    }
    
    public int min() {
        return helper.peek();
    }
}
```





#### [面试题31. 栈的压入、弹出序列](https://leetcode-cn.com/problems/zhan-de-ya-ru-dan-chu-xu-lie-lcof/)

输入两个整数序列，第一个序列表示栈的压入顺序，请判断第二个序列是否为该栈的弹出顺序。假设压入栈的所有数字均不相等。例如，序列 {1,2,3,4,5} 是某栈的压栈序列，序列 {4,5,3,2,1} 是该压栈序列对应的一个弹出序列，但 {4,3,5,1,2} 就不可能是该压栈序列的弹出序列。

 **示例 1：** 

```java
输入：pushed = [1,2,3,4,5], popped = [4,5,3,2,1]
输出：true
解释：我们可以按以下顺序执行：
push(1), push(2), push(3), push(4), pop() -> 4,
push(5), pop() -> 5, pop() -> 3, pop() -> 2, pop() -> 1

```

 **示例 2：** 

```java
输入：pushed = [1,2,3,4,5], popped = [4,3,5,1,2]
输出：false
解释：1 不能在 2 之前弹出。

```

 **思路和代码：** 

借助一个栈来模拟弹出操作，依次将pushed数组中的元素入栈，并与poped数组中元素值比较，若相等即立刻弹出，循环结束栈空则说明符合。

```java
class Solution {
    public boolean validateStackSequences(int[] pushed, int[] popped) {
        Stack<Integer> stack = new Stack<>();
        int j=0;
        for(int i=0; i< popped.length; i++) {
            stack.push(pushed[i]);
            while(!stack.isEmpty() && stack.peek()==popped[j]) {
                stack.pop();
                j++;
            }
        }
        return stack.isEmpty();
    }
}

```





#### [面试题32 - I. 从上到下打印二叉树](https://leetcode-cn.com/problems/cong-shang-dao-xia-da-yin-er-cha-shu-lcof/)

从上到下打印出二叉树的每个节点，同一层的节点按照从左到右的顺序打印。

 **例如:**
给定二叉树: `[3,9,20,null,null,15,7]`, 

```java
    3
   / \
  9  20
    /  \
   15   7
```

**返回：**

```java
[3,9,20,15,7]
```

 **思路和代码：** 

利用队列存储二叉树每一层的节点，当队列非空时将节点从头移除并加入结果集。然后按照先左后右将下一层节点加入队列。

```java
class Solution {
    public int[] levelOrder(TreeNode root) {
        if(root == null) return new int[0];
        Queue<TreeNode> queue = new LinkedList<>();
        queue.add(root);
        ArrayList<Integer> ans = new ArrayList<>();
        while(!queue.isEmpty()) {
            TreeNode node = queue.poll();
            ans.add(node.val);
            if(node.left != null) queue.add(node.left);
            if(node.right != null) queue.add(node.right);
        }
        int[] res = new int[ans.size()];
        for(int i = 0; i < ans.size(); i++)
            res[i] = ans.get(i);
        return res;
    }
}
```





#### [面试题32 - II. 从上到下打印二叉树 II](https://leetcode-cn.com/problems/cong-shang-dao-xia-da-yin-er-cha-shu-ii-lcof/)

从上到下按层打印二叉树，同一层的节点按从左到右的顺序打印，每一层打印到一行。

**例如:**
给定二叉树: `[3,9,20,null,null,15,7]`, 

```java
    3
   / \
  9  20
    /  \
   15   7
```

**返回：**

```java
[
  [3],
  [9,20],
  [15,7]
]
```

 **思路和代码：** 

 和上一题类似，只是要将每一行的数值保存到同一个list中。每次出队之前先计算当前队列的大小，这个大小就是这一层的节点数量，然后按这个数量依次从队头移除。 

```java
class Solution {
    public List<List<Integer>> levelOrder(TreeNode root) {
        LinkedList<TreeNode> queue = new LinkedList<>();
        List<List<Integer>> res = new ArrayList<>();
        if(root != null) queue.addLast(root);
        while(!queue.isEmpty()) {
            List<Integer> tmp = new ArrayList<>();
            //注意queue的size一直在变，所以每层开始从队尾取一次size值；也可以单独写个变量赋值
            for(int i=queue.size(); i>0; i--) {
                TreeNode node = queue.removeFirst();
                tmp.add(node.val);
                if(node.left != null) queue.addLast(node.left);
                if(node.right != null) queue.addLast(node.right);
            }
            res.add(tmp);
        }
        return res;
    }
}
```

DFS的递归解法参考

```java
public List<List<Integer>> levelOrder(TreeNode root) {
    List<List<Integer>> res = new ArrayList<>();
    levelHelper(res, root, 0);
    return res;
}

public void levelHelper(List<List<Integer>> list, TreeNode root, int level) {
    //边界条件判断
    if (root == null)
        return;
    //level表示的是层数，如果level >= list.size()，说明到下一层了，所以
    //要先把下一层的list初始化，防止下面add的时候出现空指针异常
    if (level >= list.size()) {
        list.add(new ArrayList<>());
    }
    //level表示的是第几层，这里访问到第几层，我们就把数据加入到第几层
    list.get(level).add(root.val);
    //当前节点访问完之后，再使用递归的方式分别访问当前节点的左右子节点
    levelHelper(list, root.left, level + 1);
    levelHelper(list, root.right, level + 1);
}
```





#### [面试题32 - III. 从上到下打印二叉树 III](https://leetcode-cn.com/problems/cong-shang-dao-xia-da-yin-er-cha-shu-iii-lcof/)

 请实现一个函数按照之字形顺序打印二叉树，即第一行按照从左到右的顺序打印，第二层按照从右到左的顺序打印，第三行再按照从左到右的顺序打印，其他行以此类推。 

**例如:**
给定二叉树: `[3,9,20,null,null,15,7]`, 

```java
    3
   / \
  9  20
    /  \
   15   7
```

**返回：**

```java
[
  [3],
  [20,9],
  [15,7]
]

```

 **思路和代码：** 

在上一题的基础上判断每一层的奇偶，利用双端队列对每层选择不同的输入方式（偶数从头进，奇数从尾进）。

```java
class Solution {
    public List<List<Integer>> levelOrder(TreeNode root) {
        Queue<TreeNode> deque = new LinkedList<>();
        List<List<Integer>> res = new ArrayList<>();
        if(root != null)
            deque.add(root);
        while(!deque.isEmpty()) {
            LinkedList<Integer> tmp = new LinkedList<>();
            for(int i= deque.size()-1; i>=0; i--) {
                TreeNode node = deque.poll();
                //res的size为当前操作所在层数减去一
                if(res.size()%2 == 1) 
                    tmp.addFirst(node.val);
                else 
                    tmp.addLast(node.val);
                if(node.left != null) deque.add(node.left);
                if(node.right != null) deque.add(node.right);
            }
            res.add(tmp);
        }
        return res;
    }
}

```

或者设置层数标识符来进行判断和逆序操作

```java
class Solution {
    public List<List<Integer>> levelOrder(TreeNode root) {
        List<List<Integer>> list = new ArrayList<>();
        if(root == null)
            return list;
        int level=1;
        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);
        while(!queue.isEmpty()){
            int n = queue.size();
            List<Integer> tmp = new ArrayList();
            for(int i=0;i<n;i++){
                TreeNode node = queue.poll();
                tmp.add(node.val);
                if(node.left != null)
                    queue.offer(node.left);
                if(node.right != null)
                    queue.offer(node.right);
            }
            if(level % 2 == 0)
                Collections.reverse(tmp);
            level++;
            list.add(tmp);
        }
        return list;
    }
}

```

DFS解法参考

```java
public List<List<Integer>> levelOrder(TreeNode root) {
    List<List<Integer>> res = new ArrayList<>();
    travel(root, res, 0);
    return res;
}

private void travel(TreeNode cur, List<List<Integer>> res, int level) {
    if (cur == null)
        return;
    //如果res.size() <= level说明下一层的集合还没创建，所以要先创建下一层的集合
    if (res.size() <= level) {
        List<Integer> newLevel = new LinkedList<>();
        res.add(newLevel);
    }
    //遍历到第几层我们就操作第几层的数据
    List<Integer> list = res.get(level);
    //这里默认根节点是第0层，偶数层相当于从左往右遍历，
    // 所以要添加到集合的末尾，如果是奇数层相当于从右往左遍历，
    // 要把数据添加到集合的开头
    if (level % 2 == 0)
        list.add(cur.val);
    else
        list.add(0, cur.val);
    //分别遍历左右两个子节点，到下一层了，所以层数要加1
    travel(cur.left, res, level + 1);
    travel(cur.right, res, level + 1);
}
```





#### [面试题33. 二叉搜索树的后序遍历序列](https://leetcode-cn.com/problems/er-cha-sou-suo-shu-de-hou-xu-bian-li-xu-lie-lcof/)

 输入一个整数数组，判断该数组是不是某二叉搜索树的后序遍历结果。如果是则返回 `true`，否则返回 `false`。假设输入的数组的任意两个数字都互不相同。 

**参考以下这颗二叉搜索树：**

```java
     5
    / \
   2   6
  / \
 1   3
```

**示例 1：**

```java
输入: [1,6,3,2,5]
输出: false
```

**示例 2：**

```java
输入: [1,3,2,6,5]
输出: true
```

 **思路和代码：** 

方法一、递归，根据后序遍历左-右-根的特点，从左边找到第一个大于根节点的值划分左右子树，左子树的值必须都比该值小（由于找到的是第一个大于根节点的值，这点肯定满足），接下来由于右子树都比根节点值大，再找到第一个不大于根节点的值，此时索引肯定等于根节点，如果不等于就是false。 

```java
class Solution {

    public boolean verifyPostorder(int[] postorder) {
        return verify(postorder, 0, postorder.length-1);
    }

    public boolean verify(int[] postorder, int i, int j) {
        if(i >= j)
            return true;
        int mid = i;
        while(postorder[mid] < postorder[j])
            mid++;
        int root = mid;
        while(postorder[root] > postorder[j])
            root++;
        if(root != j)
            return false;
        return verify(postorder,i,mid-1) && verify(postorder,mid,j-1);
    }

}
```

方法二、辅助栈，利用后续遍历的倒序，遍历数组。借助单调栈tmp存储递增节点，每当遇到递减节点时，通过出栈来更新当前节点的父节点，每轮判断当前节点和父节点的大小，大于父节点，返回false，小于则继续遍历。

```java
class Solution {
    public boolean verifyPostorder(int[] postorder) {
        Stack<Integer> tmp = new Stack<>();
        int root = Integer.MAX_VALUE;
        for(int i=postorder.length-1; i>=0; i--) {
            if(postorder[i] > root) 
                return false;
            while(!tmp.isEmpty() && tmp.peek() > postorder[i])
                root = tmp.pop();
            tmp.push(postorder[i]);
        }
        return true;
    }
}
```





#### [面试题34. 二叉树中和为某一值的路径](https://leetcode-cn.com/problems/er-cha-shu-zhong-he-wei-mou-yi-zhi-de-lu-jing-lcof/)

 输入一棵二叉树和一个整数，打印出二叉树中节点值的和为输入整数的所有路径。从树的根节点开始往下一直到叶节点所经过的节点形成一条路径。 

 **示例:**
给定如下二叉树，以及目标和 `sum = 22`， 

```java
              5
             / \
            4   8
           /   / \
          11  13  4
         /  \    / \
        7    2  5   1
```

 **返回:** 

```java
[
   [5,4,11,2],
   [5,8,4,5]
]
```

 **思路和代码：** 

回溯法，先序遍历： 按照 “根、左、右” 的顺序，遍历树的所有节点。
路径记录： 在先序遍历中，记录从根节点到当前节点的路径。当路径为 ① 根节点到叶节点形成的路径 且 ② 各节点值的和等于目标值 sum 时，将此路径加入结果列表。

```java
class Solution {
    LinkedList<Integer> tmp = new LinkedList<>();    
    List<List<Integer>> res = new ArrayList<>();
    public List<List<Integer>> pathSum(TreeNode root, int sum) {
        recur(root, sum);
        return res; 
    }

    void recur(TreeNode root, int sum) {
        if(root == null) 
            return;
        sum -= root.val;
        tmp.add(root.val);
        if(sum ==0 && root.left == null && root.right == null)
            res.add(new LinkedList(tmp));
        recur(root.left,sum);
        recur(root.right,sum);
        tmp.removeLast();
    }
}
```





#### [面试题35. 复杂链表的复制](https://leetcode-cn.com/problems/fu-za-lian-biao-de-fu-zhi-lcof/)

 请实现 `copyRandomList` 函数，复制一个复杂链表。在复杂链表中，每个节点除了有一个 `next` 指针指向下一个节点，还有一个 `random` 指针指向链表中的任意节点或者 `null`。 

 **示例 1：** 

![img](https://assets.leetcode-cn.com/aliyun-lc-upload/uploads/2020/01/09/e1.png)

```java
输入：head = [[7,null],[13,0],[11,4],[10,2],[1,0]]
输出：[[7,null],[13,0],[11,4],[10,2],[1,0]]
```

 **示例 2：** 

![img](https://assets.leetcode-cn.com/aliyun-lc-upload/uploads/2020/01/09/e2.png)

```java
输入：head = [[1,1],[2,1]]
输出：[[1,1],[2,1]]
```



 **示例 3：** 

 ![img](https://assets.leetcode-cn.com/aliyun-lc-upload/uploads/2020/01/09/e3.png)

 ```java
输入：head = [[3,null],[3,0],[3,null]]
输出：[[3,null],[3,0],[3,null]]
 ```



 **示例 4：** 

```java
输入：head = []
输出：[]
解释：给定的链表为空（空指针），因此返回 null。
```

**提示：**

- `-10000 <= Node.val <= 10000`
- `Node.random` 为空（null）或指向链表中的节点。
- 节点数目不超过 1000 。

 **思路和代码：** 

方法一、链表原地复制节点和指针，然后断开形成新链表。

```java
class Solution {
    public Node copyRandomList(Node head) {
        if (head == null)
            return head;
        // 完成链表节点的复制
        Node cur = head;
        while (cur != null) {
            Node copyNode = new Node(cur.val);
            copyNode.next = cur.next;
            cur.next = copyNode;
            cur = cur.next.next;
        }
        // 完成链表复制节点的随机指针复制
        cur = head;
        while (cur != null) {
            if (cur.random != null) // 注意判断原来的节点有没有random指针
                cur.next.random = cur.random.next;
            cur = cur.next.next;
        }
        // 将链表一分为二
        Node copyHead = head.next;
        cur = head;
        Node curCopy = head.next;
        while (cur != null) {
            cur.next = cur.next.next;
            cur = cur.next;
            if (curCopy.next != null) {
                curCopy.next = curCopy.next.next;
                curCopy = curCopy.next;
            }
        }
        return copyHead;
    }
}
```

方法二、哈希表复制

```java
class Solution {
    public Node copyRandomList(Node head) {
        if (head == null) {
            return head;
        }
        //map中存的是(原节点，拷贝节点)的一个映射
        Map<Node, Node> map = new HashMap<>();
        for (Node cur = head; cur != null; cur = cur.next) {
            map.put(cur, new Node(cur.val));
        }
        //将拷贝的新的节点组织成一个链表
        for (Node cur = head; cur != null; cur = cur.next) {
            map.get(cur).next = map.get(cur.next);
            map.get(cur).random = map.get(cur.random);
        }
        return map.get(head);
    }
}
```





#### [面试题36. 二叉搜索树与双向链表](https://leetcode-cn.com/problems/er-cha-sou-suo-shu-yu-shuang-xiang-lian-biao-lcof/)

 输入一棵二叉搜索树，将该二叉搜索树转换成一个排序的循环双向链表。要求不能创建任何新的节点，只能调整树中节点指针的指向。 

为了让您更好地理解问题，以下面的二叉搜索树为例：

![img](https://assets.leetcode.com/uploads/2018/10/12/bstdlloriginalbst.png)



 

我们希望将这个二叉搜索树转化为双向循环链表。链表中的每个节点都有一个前驱和后继指针。对于双向循环链表，第一个节点的前驱是最后一个节点，最后一个节点的后继是第一个节点。

下图展示了上面的二叉搜索树转化成的链表。“head” 表示指向链表中有最小元素的节点。

![img](https://assets.leetcode.com/uploads/2018/10/12/bstdllreturndll.png)

特别地，我们希望可以就地完成转换操作。当转化完成以后，树中节点的左指针需要指向前驱，树中节点的右指针需要指向后继。还需要返回链表中的第一个节点的指针。

 **思路和代码：** 

 是二叉搜索树，使用中序遍历从小到大遍历即可，每次遍历的时候把当前节点的left指向前一个节点，把前一个节点的right指向当前节点。 

遍历到的第一个节点就是最小节点，此时head就是它，从第二个节点开始操作，每次更新pre。

遍历完之后pre就是最后一个节点，再把它和head连起来。

```java
class Solution {
    Node pre, head;
    public Node treeToDoublyList(Node root) {
        if(root == null) return null;
        dfs(root);
        head.left = pre;
        pre.right = head;
        return head;
    }
    public void dfs(Node cur) {
        if(cur == null) 
            return;
        dfs(cur.left);
        if(pre == null)		
            //第一次操作的节点就是头节点
            head = cur;
        else
            pre.right = cur;
        cur.left = pre;
        pre = cur;
        dfs(cur.right);
    }
}
```





#### [面试题 37. 序列化二叉树](https://leetcode-cn.com/problems/xu-lie-hua-er-cha-shu-lcof/)

请实现两个函数，分别用来序列化和反序列化二叉树。

**示例:** 

```java
你可以将以下二叉树：

    1
   / \
  2   3
     / \
    4   5

序列化为 "[1,2,3,null,null,4,5]"
```

 **思路和代码：** 

层序遍历BFS，只附代码参考

```java
public class Codec {
    
    public String serialize(TreeNode root) {
        if(root == null) return "[]";
        StringBuilder res = new StringBuilder("[");
        Queue<TreeNode> queue = new LinkedList<>() {{ add(root); }};
        while(!queue.isEmpty()) {
            TreeNode node = queue.poll();
            if(node != null) {
                res.append(node.val + ",");
                queue.add(node.left);
                queue.add(node.right);
            }
            else res.append("null,");
        }
        res.deleteCharAt(res.length() - 1);
        res.append("]");
        return res.toString();
    }

    public TreeNode deserialize(String data) {
        if(data.equals("[]")) return null;
        String[] vals = data.substring(1, data.length() - 1).split(",");
        TreeNode root = new TreeNode(Integer.parseInt(vals[0]));
        Queue<TreeNode> queue = new LinkedList<>() {{ add(root); }};
        int i = 1;
        while(!queue.isEmpty()) {
            TreeNode node = queue.poll();
            if(!vals[i].equals("null")) {
                node.left = new TreeNode(Integer.parseInt(vals[i]));
                queue.add(node.left);
            }
            i++;
            if(!vals[i].equals("null")) {
                node.right = new TreeNode(Integer.parseInt(vals[i]));
                queue.add(node.right);
            }
            i++;
        }
        return root;
    }
}
```





#### [面试题38. 字符串的排列](https://leetcode-cn.com/problems/zi-fu-chuan-de-pai-lie-lcof/)

输入一个字符串，打印出该字符串中字符的所有排列。

你可以以任意顺序返回这个字符串数组，但里面不能有重复元素。

 **示例:** 

```java
输入：s = "abc"
输出：["abc","acb","bac","bca","cab","cba"]
```

**思路和代码：**

简单的回溯思想，重复方案与剪枝： 当字符串存在重复字符时，排列方案中也存在重复方案。为排除重复方案，需在固定某位字符时，保证 “每种字符只在此位固定一次” ，即遇到重复字符时不交换，直接跳过。从 DFS 角度看，此操作称为 “剪枝” 。

```java
class Solution {
    List<String> res = new ArrayList<>();
    char[] c;
    public String[] permutation(String s) {
        c =s.toCharArray();
        backtrack(0);
        return res.toArray(new String[res.size()]);
    }

    private void backtrack(int start) {
        if(start == c.length-1){
            res.add(String.valueOf(c));
            return;    
        }
        HashSet<Character> set = new HashSet<>();
        for(int i=start; i<c.length; i++) {
            if(set.contains(c[i]))
                continue;
            set.add(c[i]);
            swap(i,start);
            backtrack(start+1);
            swap(start,i);
        }
    }

    private void swap(int i, int j) {
        char tmp = c[i];
        c[i] = c[j];
        c[j] = tmp;
    }
}
```





#### [面试题39. 数组中出现次数超过一半的数字](https://leetcode-cn.com/problems/shu-zu-zhong-chu-xian-ci-shu-chao-guo-yi-ban-de-shu-zi-lcof/)

数组中有一个数字出现的次数超过数组长度的一半，请找出这个数字。

你可以假设数组是非空的，并且给定的数组总是存在多数元素。

 **示例 1:** 

```java
输入: [1, 2, 3, 2, 2, 2, 5, 4, 2]
输出: 2
```

**限制：**

```java
1 <= 数组长度 <= 50000
```

 **思路和代码：** 

摩尔投票法：

- 票数和： 由于众数出现的次数超过数组长度的一半；若记 众数 的票数为 `+1` ，非众数 的票数为 `-1` ，则一定有所有数字的 票数和 `> 0` 。
- 票数正负抵消： 设数组 `nums` 中的众数为 `x` ，数组长度为 `n` 。若 nums 的前 `a` 个数字的 票数和 `= 0` ，则 数组后 `(n-a)` 个数字的 票数和一定仍 `> 0` （即后 `(n−a)` 个数字的 众数仍为 `x`)。

```java
class Solution {
    public int majorityElement(int[] nums) {
        int cnt = 0, res = 0;
        for(int num : nums) {
            if(cnt == 0) 
                res = num;
            if(res == num) 
                cnt++;
            else 
                cnt--;
        }
        return res;
    }
}
```





#### [面试题40. 最小的k个数](https://leetcode-cn.com/problems/zui-xiao-de-kge-shu-lcof/)

 输入整数数组 `arr` ，找出其中最小的 `k` 个数。例如，输入4、5、1、6、2、7、3、8这8个数字，则最小的4个数字是1、2、3、4。 

 **示例 1：** 

```java
输入：arr = [3,2,1], k = 2
输出：[1,2] 或者 [2,1]
```



 **示例 2：** 

```java
输入：arr = [0,1,2,1], k = 1
输出：[0]
```

 **思路和代码：** 

[TopK问题解决方案]( https://leetcode-cn.com/problems/zui-xiao-de-kge-shu-lcof/solution/3chong-jie-fa-miao-sha-topkkuai-pai-dui-er-cha-sou/ )

总结的很好

```java
//计数排序的方法
class Solution {
    public int[] getLeastNumbers(int[] arr, int k) {
        if(arr.length == 0 || k == 0) return new int[0];
        int[] cnt = new int[10001];
        for(int num : arr) {
            cnt[num]++;
        } 
        int[] res = new int[k];
        int index = 0;
        for(int i=0; i<cnt.length; i++) {
            while(cnt[i]-- > 0 && index < k) {
                res[index++] = i;
            }
            if(index == k)
                break;
        }
        return res;
    }
}
```

