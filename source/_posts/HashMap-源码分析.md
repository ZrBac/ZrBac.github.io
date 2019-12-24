---
title: HashMap 源码分析
date: 2019-12-23 10:09:22
tags:
- Java
categories: 数据结构
---

## HashMap概述

HashMap时常用的Java集合之一，是基于哈希表的Map接口的实现。HashMap的底层是哈希数组，数组元素为Entry，HashMap通过key的hashCode来计算hash值，当hashCode相同时，通过“拉链法”解决冲突。


## HashMap数据结构

在jdk1.8之后，解决哈希冲突的方式有了较大变化，当链表长度大于阈值(默认为8)时，将链表转化为红黑树，以减少搜索时间，原本Map.Entry接口的实现类Entry改名为Node，转化为红黑树时改用另一种实现TreeNode。

**Node类**
```java
static class Node<K,V> implements Map.Entry<K,V> {
        final int hash; // 哈希值
        final K key;
        V value;
        Node<K,V> next; // 指向下一个节点

        Node(int hash, K key, V value, Node<K,V> next) {
            this.hash = hash;
            this.key = key;
            this.value = value;
            this.next = next;
        }

        public final K getKey()        { return key; }
        public final V getValue()      { return value; }
        public final String toString() { return key + "=" + value; }

        public final int hashCode() {
            return Objects.hashCode(key) ^ Objects.hashCode(value);
        }

        public final V setValue(V newValue) {
            V oldValue = value;
            value = newValue;
            return oldValue;
        }

        public final boolean equals(Object o) {
            if (o == this)
                return true;
            if (o instanceof Map.Entry) {
                Map.Entry<?,?> e = (Map.Entry<?,?>)o;
                if (Objects.equals(key, e.getKey()) &&
                    Objects.equals(value, e.getValue()))
                    return true;
            }
            return false;
        }
    }
```

**TreeNode类**
```java
static final class TreeNode<K,V> extends LinkedHashMap.Entry<K,V> {
        TreeNode<K,V> parent;  // red-black tree links
        TreeNode<K,V> left;
        TreeNode<K,V> right;
        TreeNode<K,V> prev;    // needed to unlink next upon deletion
        boolean red;
        TreeNode(int hash, K key, V val, Node<K,V> next) {
            super(hash, key, val, next);
        }
    }
```

HashMap就是这样一个Entry（包括Node和TreeNode）数组，Node对象中包含键、值和hash值，next指向下一个Entry，用来处理哈希冲突。TreeNode对象包含指向父节点、子节点和前一个节点（移除对象时使用）的指针，以及表示红黑节点的boolean标识。


## HashMap源码分析

### 1、定位哈希桶数组索引位置

不管增加、删除、查找键值对，定位到哈希桶数组的位置都是很关键的第一步。前面说过HashMap的数据结构是“数组+链表+红黑树”的结合，所以我们当然希望这个HashMap里面的元素位置尽量分布均匀些，尽量使得每个位置上的元素数量只有一个，那么当我们用hash算法求得这个位置的时候，马上就可以知道对应位置的元素就是我们要的，不用遍历链表/红黑树，大大优化了查询的效率。HashMap定位数组索引位置，直接决定了hash方法的离散性能。
```java
// 代码1
static final int hash(Object key) { // 计算key的hash值
int h;
// 1.先拿到key的hashCode值; 2.将hashCode的高16位参与运算
return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
// 代码2
int n = tab.length;
// 将(tab.length - 1) 与 hash值进行&运算
int index = (n - 1) & hash;
/*整个过程本质上就是三步：
拿到key的hashCode值
将hashCode的高位参与运算，重新计算hash值
将计算出来的hash值与(table.length - 1)进行&运算
*/
```

方法解读：

对于任意给定的对象，只要它的hashCode()返回值相同，那么计算得到的hash值总是相同的。我们首先想到的就是把hash值对table长度取模运算，这样一来，元素的分布相对来说是比较均匀的。

但是模运算消耗还是比较大的，我们知道计算机比较快的运算为位运算，因此JDK团队对取模运算进行了优化，使用上面代码2的位与运算来代替模运算。这个方法非常巧妙，它通过 "(table.length -1) & h" 来得到该对象的索引位置，这个优化是基于以下公式：x mod 2^n = x & (2^n - 1)。我们知道HashMap底层数组的长度总是2的n次方，并且取模运算为"h mod table.length"，对应上面的公式，可以得到该运算等同于"h & (table.length - 1)"。这是HashMap在速度上的优化，因为&比%具有更高的效率。

在JDK1.8的实现中，还优化了高位运算的算法，将hashCode的高16位与hashCode进行异或运算，主要是为了在table的length较小的时候，让高位也参与运算，并且不会有太大的开销

### 2、主要属性
```java
transient Node<K,V>[] table;            //哈希数组
transient Set<Map.Entry<K,V>> entrySet  //entry缓存Set
transient int size;                     //元素个数
transient int modCount;                 //修改次数
int threhold;     //阈值，等于加载因子*容量，当实际大小超过阈值时进行扩容
final float loadFactor;                 //加载因子，默认为0.75 
```

### 3、构造方法
```java
/**
     * 根据初始化容量和加载因子构建一个空的HashMap.
     */
    public HashMap(int initialCapacity, float loadFactor) {
        if (initialCapacity < 0)
            throw new IllegalArgumentException("Illegal initial capacity: " +
                                               initialCapacity);
        if (initialCapacity > MAXIMUM_CAPACITY)
            initialCapacity = MAXIMUM_CAPACITY;
        if (loadFactor <= 0 || Float.isNaN(loadFactor))
            throw new IllegalArgumentException("Illegal load factor: " +
                                               loadFactor);
        this.loadFactor = loadFactor;
        this.threshold = tableSizeFor(initialCapacity);
    }

    /**
     * 使用初始化容量和默认加载因子(0.75).
     */
    public HashMap(int initialCapacity) {
        this(initialCapacity, DEFAULT_LOAD_FACTOR);
    }

    /**
     * 使用默认初始化大小(16)和默认加载因子(0.75).
     */
    public HashMap() {
        this.loadFactor = DEFAULT_LOAD_FACTOR; // all other fields defaulted
    }

    /**
     * 用已有的Map构造一个新的HashMap.
     */
    public HashMap(Map<? extends K, ? extends V> m) {
        this.loadFactor = DEFAULT_LOAD_FACTOR;
        putMapEntries(m, false);
    }
```

### 4、数据存取

**`putAll`方法**
```java
public void putAll(Map<? extends K, ? extends V> m) {
        putMapEntries(m, true);
    }

    /**
     * Implements Map.putAll and Map constructor
     *
     * @param m the map
     * @param evict false when initially constructing this map, else
     * true (relayed to method afterNodeInsertion).
     */
    final void putMapEntries(Map<? extends K, ? extends V> m, boolean evict) {
        int s = m.size();
        if (s > 0) {
            if (table == null) { // pre-size
                float ft = ((float)s / loadFactor) + 1.0F;
                int t = ((ft < (float)MAXIMUM_CAPACITY) ?
                         (int)ft : MAXIMUM_CAPACITY);
                if (t > threshold)
                    threshold = tableSizeFor(t);
            }
            else if (s > threshold)
                resize();
            for (Map.Entry<? extends K, ? extends V> e : m.entrySet()) {
                K key = e.getKey();
                V value = e.getValue();
                putVal(hash(key), key, value, false, evict); // put核心方法
            }
        }
    }
```

**`put`方法**
```java
public V put(K key, V value) {
        return putVal(hash(key), key, value, false, true);
    }

final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
                   boolean evict) {
        Node<K,V>[] tab; Node<K,V> p; int n, i;
        if ((tab = table) == null || (n = tab.length) == 0) // table为空或length为0
            n = (tab = resize()).length; // 初始化
        if ((p = tab[i = (n - 1) & hash]) == null) // 如果hash所在位置为null，直接put
            tab[i] = newNode(hash, key, value, null);
        else { // tab[i]有元素，遍历节点后添加
            Node<K,V> e; K k;
            // 如果hash、key都相等，直接覆盖
            if (p.hash == hash &&
                ((k = p.key) == key || (key != null && key.equals(k))))
                e = p;
            else if (p instanceof TreeNode) // 红黑树添加节点
                e = ((TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
            else { // 链表
                for (int binCount = 0; ; ++binCount) {
                    if ((e = p.next) == null) { // 找到链表最后一个节点，插入新节点
                        p.next = newNode(hash, key, value, null);
                        // 链表节点大于阈值8，调用treeifyBin方法，当tab.length大于64将链表改为红黑树
                        // 如果tab.length < 64或tab为null，则调用resize方法重构链表.
                        if (binCount >= TREEIFY_THRESHOLD - 1) // -1 for 1st
                            treeifyBin(tab, hash);
                        break;
                    }
                    // hash、key都相等，此时节点即要更新节点
                    if (e.hash == hash &&
                        ((k = e.key) == key || (key != null && key.equals(k))))
                        break;
                    p = e;
                }
            }
            // 当前节点e = p.next不为null，表示链表中原本存在相同的key，则返回oldValue
            if (e != null) { // existing mapping for key
                V oldValue = e.value;
                // onlyIfAbsent值为false，参数主要决定存在相同key时是否执行替换
                if (!onlyIfAbsent || oldValue == null)
                    e.value = value;
                afterNodeAccess(e);
                return oldValue;
            }
        }
        ++modCount;
        if (++size > threshold) // 检查是否超过阈值
            resize();
        afterNodeInsertion(evict);
        return null; // 原HashMap中不存在相同的key，插入键值对后返回null
    }
```

**`treeifyBin`方法**
```java
final void treeifyBin(Node<K,V>[] tab, int hash) {
        int n, index; Node<K,V> e;
        //当tab为null或tab.length<64需要进行扩容
        if (tab == null || (n = tab.length) < MIN_TREEIFY_CAPACITY)
            resize();
        else if ((e = tab[index = (n - 1) & hash]) != null) {
            TreeNode<K,V> hd = null, tl = null;
            do {
                TreeNode<K,V> p = replacementTreeNode(e, null);
                if (tl == null)
                    hd = p;
                else {
                    p.prev = tl;
                    tl.next = p;
                }
                tl = p;
            } while ((e = e.next) != null);
            if ((tab[index] = hd) != null)
                //存储在红黑树
                hd.treeify(tab);
        }
    }
```

### 5、get查找

```java
public V get(Object key) {
        Node<K,V> e;
        return (e = getNode(hash(key), key)) == null ? null : e.value;
    }

    /**
     * Implements Map.get and related methods
     *
     * @param hash hash for key
     * @param key the key
     * @return the node, or null if none
     */
    final Node<K,V> getNode(int hash, Object key) {
        Node<K,V>[] tab; Node<K,V> first, e; int n; K k;
        if ((tab = table) != null && (n = tab.length) > 0 &&
            (first = tab[(n - 1) & hash]) != null) {
            if (first.hash == hash && // always check first node
                ((k = first.key) == key || (key != null && key.equals(k))))
                return first;
            if ((e = first.next) != null) {
                if (first instanceof TreeNode)
                    return ((TreeNode<K,V>)first).getTreeNode(hash, key);
                do {
                    if (e.hash == hash &&
                        ((k = e.key) == key || (key != null && key.equals(k))))
                        return e;
                } while ((e = e.next) != null);
            }
        }
        return null;
    }
```

### 6、resize扩容
```java
/**
     * Initializes or doubles table size.  If null, allocates in
     * accord with initial capacity target held in field threshold.
     * Otherwise, because we are using power-of-two expansion, the
     * elements from each bin must either stay at same index, or move
     * with a power of two offset in the new table.
     *
     * @return the table
     */
    final Node<K,V>[] resize() {
        Node<K,V>[] oldTab = table;
        int oldCap = (oldTab == null) ? 0 : oldTab.length;
        int oldThr = threshold;
        int newCap, newThr = 0;
        if (oldCap > 0) {
            if (oldCap >= MAXIMUM_CAPACITY) {
                threshold = Integer.MAX_VALUE;
                return oldTab;
            }
            else if ((newCap = oldCap << 1) < MAXIMUM_CAPACITY &&
                     oldCap >= DEFAULT_INITIAL_CAPACITY)
                newThr = oldThr << 1; // double threshold
        }
        else if (oldThr > 0) // initial capacity was placed in threshold
            newCap = oldThr;
        else {               // zero initial threshold signifies using defaults
            newCap = DEFAULT_INITIAL_CAPACITY;
            newThr = (int)(DEFAULT_LOAD_FACTOR * DEFAULT_INITIAL_CAPACITY);
        }
        if (newThr == 0) {
            float ft = (float)newCap * loadFactor;
            newThr = (newCap < MAXIMUM_CAPACITY && ft < (float)MAXIMUM_CAPACITY ?
                      (int)ft : Integer.MAX_VALUE);
        }
        threshold = newThr;
        @SuppressWarnings({"rawtypes","unchecked"})
            Node<K,V>[] newTab = (Node<K,V>[])new Node[newCap];
        table = newTab;
        if (oldTab != null) {
            for (int j = 0; j < oldCap; ++j) {
                Node<K,V> e;
                if ((e = oldTab[j]) != null) {
                    oldTab[j] = null;
                    if (e.next == null)
                        newTab[e.hash & (newCap - 1)] = e;
                    else if (e instanceof TreeNode)
                        ((TreeNode<K,V>)e).split(this, newTab, j, oldCap);
                    else { // preserve order
                        Node<K,V> loHead = null, loTail = null;
                        Node<K,V> hiHead = null, hiTail = null;
                        Node<K,V> next;
                        do {
                            next = e.next;
                            if ((e.hash & oldCap) == 0) {
                                if (loTail == null)
                                    loHead = e;
                                else
                                    loTail.next = e;
                                loTail = e;
                            }
                            else {
                                if (hiTail == null)
                                    hiHead = e;
                                else
                                    hiTail.next = e;
                                hiTail = e;
                            }
                        } while ((e = next) != null);
                        if (loTail != null) {
                            loTail.next = null;
                            newTab[j] = loHead;
                        }
                        if (hiTail != null) {
                            hiTail.next = null;
                            //把节点移动新的位置j+oldCap,这种情况不适用与链表的节点数大于8的情况
                            //链表节点大于8的情况会转换为红黑树存储
                            newTab[j + oldCap] = hiHead;
                        }
                    }
                }
            }
        }
        return newTab;
    }
```

### 7、HashMap红黑树存储
```java
final void treeify(Node<K,V>[] tab) {
            TreeNode<K,V> root = null;
            for (TreeNode<K,V> x = this, next; x != null; x = next) {
                next = (TreeNode<K,V>)x.next;
                x.left = x.right = null;
                if (root == null) {
                    x.parent = null;
                    x.red = false;
                    root = x;
                }
                else {
                    K k = x.key;
                    int h = x.hash;
                    Class<?> kc = null;
                    //遍历root，把节点x插入到红黑树中，执行先插入，然后进行红黑树修正
                    for (TreeNode<K,V> p = root;;) {
                        int dir, ph;
                        K pk = p.key;
                        if ((ph = p.hash) > h)
                            dir = -1;
                        else if (ph < h)
                            dir = 1;
                        else if ((kc == null &&
                                  (kc = comparableClassFor(k)) == null) ||
                                 (dir = compareComparables(kc, k, pk)) == 0)
                            dir = tieBreakOrder(k, pk);//比较k和pk的值，用于判断是遍历左子树还是右子树
                        TreeNode<K,V> xp = p;
                        if ((p = (dir <= 0) ? p.left : p.right) == null) {
                            x.parent = xp;
                            if (dir <= 0)
                                xp.left = x;
                            else
                                xp.right = x;
                            //修正红黑树
                            root = balanceInsertion(root, x);
                            //退出循环
                            break;
                        }
                    }
                }
            }
            moveRootToFront(tab, root);
        }
```

上面主要做的是红黑树的insert，我们知道红黑树insert后是需要修复的，为了保持红黑树的平衡，我们来看下红黑树平衡的几条性质：
- 节点是红色或黑色。
- 根是黑色。
- 所有叶子都是黑色（叶子是NULL节点）。
- 每个红色节点必须有两个黑色的子节点。（从每个叶子到根的所有路径上不能有两个连续的红色节点。）
- 从任一节点到其每个叶子的所有简单路径都包含相同数目的黑色节点。

当insert一个节点之后为了达到平衡，我们可能需要对节点进行旋转和颜色翻转（上面的balanceInsertion方法）。
```java
static <K,V> TreeNode<K,V> balanceInsertion(TreeNode<K,V> root,
                                                    TreeNode<K,V> x) {
            //插入的节点必须是红色的，除非是根节点                                            
            x.red = true;
            //遍历到x节点为黑色,整个过程是一个上滤的过程
            //xp=x.parent;xpp=xp.parent;xppl=xpp.left;xppr=xpp.right;
            for (TreeNode<K,V> xp, xpp, xppl, xppr;;) {
                if ((xp = x.parent) == null) {
                    x.red = false;
                    return x;
                }
                //如果xp的黑色就直接完成，最简单的情况
                else if (!xp.red || (xpp = xp.parent) == null)
                    return root;
                //如果x的父节点是x父节点的左节点
                if (xp == (xppl = xpp.left)) {
                    //x的父亲节点的兄弟是红色的（需要颜色翻转）
                    if ((xppr = xpp.right) != null && xppr.red) {
                        //x父亲节点的兄弟节点置成黑色
                        xppr.red = false;
                        //父几点和其兄弟节点一样是黑色
                        xp.red = false;
                        //祖父节点置成红色
                        xpp.red = true;
                        //然后上滤（就是不断的重复上面的操作）
                        x = xpp;
                    }
                    else {
                        //如果x是xp的右节点整个要进行两次旋转,先左旋转再右旋转
                        if (x == xp.right) {
                            root = rotateLeft(root, x = xp);
                            xpp = (xp = x.parent) == null ? null : xp.parent;
                        }
                        if (xp != null) {
                            xp.red = false;
                            if (xpp != null) {
                                xpp.red = true;
                                root = rotateRight(root, xpp);
                            }
                        }
                    }
                }
                //以左节点镜像对称就不做具体分析了 
                else {
                    if (xppl != null && xppl.red) {
                        xppl.red = false;
                        xp.red = false;
                        xpp.red = true;
                        x = xpp;
                    }
                    else {
                        if (x == xp.left) {
                            root = rotateRight(root, x = xp);
                            xpp = (xp = x.parent) == null ? null : xp.parent;
                        }
                        if (xp != null) {
                            xp.red = false;
                            if (xpp != null) {
                                xpp.red = true;
                                root = rotateLeft(root, xpp);
                            }
                        }
                    }
                }
            }
        }
```


