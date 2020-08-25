---
title: ArrayList源码分析
date: 2020-08-25 11:29:49
tags:
- Java
categories: 数据结构
---

# ArrayList源码分析

## 类图

![img]( http://qiniu.zrbac.fun/26.png)

- 实现了`RandomAccess`接口，可以随机访问
- 实现了`Cloneable`接口，可以克隆
- 实现了`Serializable`接口，可以序列化、反序列化
- 实现了`List`接口，是`List`的实现类之一
- 实现了`Collection`接口，是`Java Collections Framework`成员之一
- 实现了`Iterable`接口，可以使用`for-each`迭代

## 属性

```java
// 序列化版本UID
private static final long
        serialVersionUID = 8683452581122892189L;

/**
 * 默认的初始容量
 */
private static final int
        DEFAULT_CAPACITY = 10;

/**
 * 用于空实例的共享空数组实例
 * new ArrayList(0);
 */
private static final Object[]
        EMPTY_ELEMENTDATA = {};

/**
 * 用于提供默认大小的实例的共享空数组实例
 * new ArrayList();
 */
private static final Object[]
        DEFAULTCAPACITY_EMPTY_ELEMENTDATA = {};

/**
 * 存储ArrayList元素的数组缓冲区
 * ArrayList的容量，是数组的长度
 * 
 * non-private to simplify nested class access
 */
transient Object[] elementData;

/**
 * ArrayList中元素的数量
 */
private int size;
```

<!--more-->

1. 为什么空实例默认数组有的时候是`EMPTY_ELEMENTDATA`，而又有的时候是`DEFAULTCAPACITY_EMPTY_ELEMENTDATA`
2. 为什么`elementData`要被`transient`修饰
3. 为什么`elementData`没有被`private`修饰？难道正如注释所写的**non-private to simplify nested class access**

## 构造方法

### 带初始容量的构造方法

```java
/**
 * 带一个初始容量参数的构造方法
 *
 * @param  initialCapacity  初始容量
 * @throws  如果初始容量非法就抛出
 *          IllegalArgumentException
 */
public ArrayList(int initialCapacity) {
    if (initialCapacity > 0) {
        this.elementData =
                new Object[initialCapacity];
    } else if (initialCapacity == 0) {
        this.elementData = EMPTY_ELEMENTDATA;
    } else {
        throw new IllegalArgumentException(
                "Illegal Capacity: "+ initialCapacity);
    }
}
```

- 如果`initialCapacity < 0`，就创建一个新的长度是`initialCapacity`的数组
- 如果`initialCapacity == 0`，就使用EMPTY_ELEMENTDATA
- 其他情况，`initialCapacity`不合法，抛出异常

### 无参构造方法

```java
/**
 * 无参构造方法 将elementData 赋值为
 *   DEFAULTCAPACITY_EMPTY_ELEMENTDATA
 */
public ArrayList() {
    this.elementData =
            DEFAULTCAPACITY_EMPTY_ELEMENTDATA;
}
```

### 带一个集合参数的构造方法

```java
/**
 * 带一个集合参数的构造方法
 *
 * @param c 集合，代表集合中的元素会被放到list中
 * @throws 如果集合为空，抛出NullPointerException
 */
public ArrayList(Collection<? extends E> c) {
    elementData = c.toArray();
    // 如果 size != 0
    if ((size = elementData.length) != 0) {
        // c.toArray 可能不正确的，不返回 Object[]
        // https://bugs.openjdk.java.net/browse/JDK-6260652
        if (elementData.getClass() != Object[].class)
            elementData = Arrays.copyOf(
                    elementData, size, Object[].class);
    } else {
        // size == 0
        // 将EMPTY_ELEMENTDATA 赋值给 elementData
        this.elementData = EMPTY_ELEMENTDATA;
    }
}
```

- 使用将集合转换为数组的方法
- 为了防止`c.toArray()`方法不正确的执行，导致没有返回`Object[]`，特殊做了处理
- 如果数组大小等于`0`，则使用 `EMPTY_ELEMENTDATA`

> 那么问题来了，什么情况下`c.toArray()`会不返回`Object[]`呢？

```java
public static void main(String[] args) {
    List<String> list = new ArrayList<>(Arrays.asList("list"));
    // class java.util.ArrayList
    System.out.println(list.getClass());

    Object[] listArray = list.toArray();
    // class [Ljava.lang.Object;
    System.out.println(listArray.getClass());
    listArray[0] = new Object();

    System.out.println();

    List<String> asList = Arrays.asList("asList");
    // class java.util.Arrays$ArrayList
    System.out.println(asList.getClass());

    Object[] asListArray = asList.toArray();
    // class [Ljava.lang.String;
    System.out.println(asListArray.getClass());
    // java.lang.ArrayStoreException
    asListArray[0] = new Object();
}
```

我们通过这个例子可以看出来，`java.util.ArrayList.toArray()`方法会返回`Object[]`没有问题。而`java.util.Arrays`的私有内部类ArrayList的`toArray()`方法可能不返回`Object[]`。

> 为什么会这样？

我们看ArrayList的`toArray()`方法源码：

```java
public Object[] toArray() {
    // ArrayLisy中 elementData是这样定义的
    // transient Object[] elementData;
    return Arrays.copyOf(elementData, size);
}
```

使用了`Arrays.copyOf()`方法：

```java
public static <T> T[] copyOf(T[] original, int newLength) {
    // original.getClass() 是 class [Ljava.lang.Object
    return (T[]) copyOf(original, newLength, original.getClass());
}
```

`copyOf()`的具体实现：

```java
public static <T,U> T[] copyOf(U[] original, 
          int newLength, Class<? extends T[]> newType) {
    @SuppressWarnings("unchecked")
    /**
     * 如果newType是Object[] copy 数组 类型就是 Object 
     * 否则就是 newType 类型
     */
    T[] copy = ((Object)newType == (Object)Object[].class)
        ? (T[]) new Object[newLength]
        : (T[]) Array.newInstance(newType.getComponentType(), newLength);
    System.arraycopy(original, 0, copy, 0,
                     Math.min(original.length, newLength));
    return copy;
}
```

我们知道ArrayList中`elementData`就是`Object[]`类型，所以ArrayList的`toArray()`方法必然会返回`Object[]`。

我们再看一下`java.util.Arrays`的内部ArrayList源码（截取的部分源码）：

```java
private static class ArrayList<E> extends AbstractList<E>
        implements RandomAccess, java.io.Serializable {

    // 存储元素的数组
    private final E[] a;

    ArrayList(E[] array) {
        // 直接把接收的数组 赋值 给 a
        a = Objects.requireNonNull(array);
    }

    /**
     * obj 为空抛出异常
     * 不为空 返回 obj
     */
    public static <T> T requireNonNull(T obj) {
        if (obj == null)
            throw new NullPointerException();
        return obj;
    }

    @Override
    public Object[] toArray() {
        // 返回 a 的克隆对象
        return a.clone();
    }

}
```

这是`Arrays.asList()`方法源码

```java
public static <T> List<T> asList(T... a) {
    return new ArrayList<>(a);
}
```

不难看出来`java.util.Arrays`的内部ArrayList的`toArray()`方法，是构造方法接收什么类型的数组，就返回什么类型的数组。

所以，在我们上面的例子中，实际上返回的是String类型的数组，再将其中的元素赋值成`Object`类型的，自然报错。

我们还是继续看ArrayList吧…

## 插入方法

### 在列表最后添加指定元素

```java
/**
 * 在列表最后添加指定元素
 *
 * @param e 要添加的指定元素
 * @return true
 */
public boolean add(E e) {
    // 增加 modCount ！！
    ensureCapacityInternal(size + 1); 
    elementData[size++] = e;
    return true;
}
```

- 在父类`AbstractList`上，定义了`modCount` 属性，用于记录数组修改的次数。

### 在指定位置添加指定元素

```java
/**
 * 在指定位置添加指定元素
 * 如果指定位置已经有元素，就将该元素和随后的元素移动到右面一位
 *
 * @param index 待插入元素的下标
 * @param element 待插入的元素
 * @throws 可能抛出 IndexOutOfBoundsException
 */
public void add(int index, E element) {
    rangeCheckForAdd(index);


    // 增加 modCount ！！
    ensureCapacityInternal(size + 1);
    System.arraycopy(elementData, index, elementData, index + 1,
                     size - index);
    elementData[index] = element;
    size++;
}
```

### 插入方法调用的其他私有方法

```java
/**
 * 计算容量
 */
private static int calculateCapacity(
        Object[] elementData, int minCapacity) {

    if (elementData ==
            DEFAULTCAPACITY_EMPTY_ELEMENTDATA) {
        return Math.max(DEFAULT_CAPACITY, minCapacity);
    }
    return minCapacity;
}

private void ensureCapacityInternal(int minCapacity) {
    ensureExplicitCapacity(
            calculateCapacity(elementData, minCapacity)
    );
}

private void ensureExplicitCapacity(int minCapacity) {
    modCount++;

    // overflow-conscious code
    if (minCapacity - elementData.length > 0)
        grow(minCapacity);
}/** * 计算容量 */private static int calculateCapacity(        Object[] elementData, int minCapacity) {    if (elementData ==            DEFAULTCAPACITY_EMPTY_ELEMENTDATA) {        return Math.max(DEFAULT_CAPACITY, minCapacity);    }    return minCapacity;}private void ensureCapacityInternal(int minCapacity) {    ensureExplicitCapacity(            calculateCapacity(elementData, minCapacity)    );}private void ensureExplicitCapacity(int minCapacity) {    modCount++;    // overflow-conscious code    if (minCapacity - elementData.length > 0)        grow(minCapacity);}
```

## 扩容方法

```java
/**
 * 数组可以分配的最大size
 * 一些虚拟机在数组中预留一些header words
 * 如果尝试分配更大的size，可能导致OutOfMemoryError
 */
private static final int MAX_ARRAY_SIZE = Integer.MAX_VALUE - 8;

/**
 * 增加容量，至少保证比minCapacity大
 * @param minCapacity 期望的最小容量
 */
private void grow(int minCapacity) {
    // 有可能溢出的代码
    int oldCapacity = elementData.length;
    int newCapacity = oldCapacity + (oldCapacity >> 1);
    if (newCapacity - minCapacity < 0)
        newCapacity = minCapacity;
    if (newCapacity - MAX_ARRAY_SIZE > 0)
        newCapacity = hugeCapacity(minCapacity);
    // minCapacity is usually close to size, so this is a win:
    elementData = Arrays.copyOf(elementData, newCapacity);
}

/**
 * 最大容量返回 Integer.MAX_VALUE
 */
private static int hugeCapacity(int minCapacity) {
    if (minCapacity < 0) // overflow
        throw new OutOfMemoryError();
    return (minCapacity > MAX_ARRAY_SIZE) ?
        Integer.MAX_VALUE :
        MAX_ARRAY_SIZE;
}
```

- 通常情况新容量是原来容量的1.5倍
- 如果原容量的1.5倍比`minCapacity`小，那么就扩容到`minCapacity`
- 特殊情况扩容到`Integer.MAX_VALUE`

> 看完构造方法、添加方法、扩容方法之后，上文第1个问题终于有了答案。原来，`new ArrayList()`会将`elementData` 赋值为 DEFAULTCAPACITY_EMPTY_ELEMENTDATA，`new ArrayList(0)`会将`elementData` 赋值为 EMPTY_ELEMENTDATA，EMPTY_ELEMENTDATA添加元素会扩容到容量为`1`，而DEFAULTCAPACITY_EMPTY_ELEMENTDATA扩容之后容量为`10`。

通过反射我们可以验证这一想法。如下：

```java
public static void main(String[] args) {
    printDefaultCapacityList();
    printEmptyCapacityList();
}

public static void printDefaultCapacityList() {
    ArrayList defaultCapacity = new ArrayList();
    System.out.println(
            "default 初始化长度：" + getCapacity(defaultCapacity));

    defaultCapacity.add(1);
    System.out.println(
            "default add 之后 长度：" + getCapacity(defaultCapacity));
}

public static void printEmptyCapacityList() {
    ArrayList emptyCapacity = new ArrayList(0);
    System.out.println(
            "empty 初始化长度：" + getCapacity(emptyCapacity));

    emptyCapacity.add(1);
    System.out.println(
            "empty add 之后 长度：" + getCapacity(emptyCapacity));
}

public static int getCapacity(ArrayList<?> arrayList) {
    Class<ArrayList> arrayListClass = ArrayList.class;
    try {
        // 获取 elementData 字段
        Field field = arrayListClass.getDeclaredField("elementData");
        // 开启访问权限
        field.setAccessible(true);
        // 把示例传入get，获取实例字段elementData的值
        Object[] objects = (Object[]) field.get(arrayList);
        //返回当前ArrayList实例的容量值
        return objects.length;
    } catch (Exception e) {
        e.printStackTrace();
        return -1;
    }
}
```

## 移除方法

### 移除指定下标元素方法

```java
/**
 * 移除列表中指定下标位置的元素
 * 将所有的后续元素，向左移动
 *
 * @param 要移除的指定下标
 * @return 返回被移除的元素
 * @throws 下标越界会抛出IndexOutOfBoundsException
 */
public E remove(int index) {
    rangeCheck(index);

    modCount++;
    E oldValue = elementData(index);

    int numMoved = size - index - 1;
    if (numMoved > 0)
            System.arraycopy(elementData, 
                    index+1, elementData, index,  numMoved);
    // 将引用置空，让GC回收
    elementData[--size] = null;

    return oldValue;
}
```

### 移除指定元素方法

```java
/**
 * 移除第一个在列表中出现的指定元素
 * 如果存在，移除返回true
 * 否则，返回false
 *
 * @param o 指定元素
 */
public boolean remove(Object o) {
    if (o == null) {
        for (int index = 0; index < size; index++)
            if (elementData[index] == null) {
                fastRemove(index);
                return true;
            }
    } else {
        for (int index = 0; index < size; index++)
            if (o.equals(elementData[index])) {
                fastRemove(index);
                return true;
            }
    }
    return false;
}
```

> 移除方法名字、参数的个数都一样，使用的时候要注意。

### 私有移除方法

```java
/*
 * 私有的 移除 方法 跳过边界检查且不返回移除的元素
 */
private void fastRemove(int index) {
    modCount++;
    int numMoved = size - index - 1;
    if (numMoved > 0)
        System.arraycopy(elementData, index+1, elementData, index,
                         numMoved);
    // 将引用置空，让GC回收
    elementData[--size] = null;
}
```

## 查找方法

### 查找指定元素的所在位置

```java
/**
 * 返回指定元素第一次出现的下标
 * 如果不存在该元素，返回 -1
 * 如果 o ==null 会特殊处理
 */
public int indexOf(Object o) {
    if (o == null) {
        for (int i = 0; i < size; i++)
            if (elementData[i]==null)
                return i;
    } else {
        for (int i = 0; i < size; i++)
            if (o.equals(elementData[i]))
                return i;
    }
    return -1;
}
```

### 查找指定位置的元素

```java
/**
 * 返回指定位置的元素
 *
 * @param  index 指定元素的位置 
 * @throws index越界会抛出IndexOutOfBoundsException
 */
public E get(int index) {
    rangeCheck(index);

    return elementData(index);
}
```

> 该方法直接返回`elementData`数组指定下标的元素，效率还是很高的。所以ArrayList，`for`循环遍历效率也是很高的。

## 序列化方法

```java
/**
 * 将ArrayLisy实例的状态保存到一个流里面
 */
private void writeObject(java.io.ObjectOutputStream s)
    throws java.io.IOException{
    // Write out element count, and any hidden stuff
    int expectedModCount = modCount;
    s.defaultWriteObject();

    // Write out size as capacity for behavioural compatibility with clone()
    s.writeInt(size);

    // 按照顺序写入所有的元素
    for (int i=0; i<size; i++) {
        s.writeObject(elementData[i]);
    }

    if (modCount != expectedModCount) {
        throw new ConcurrentModificationException();
    }
}
```

## 反序列化方法

```java
/**
 * 根据一个流(参数)重新生成一个ArrayList
 */
private void readObject(java.io.ObjectInputStream s)
    throws java.io.IOException, ClassNotFoundException {
    elementData = EMPTY_ELEMENTDATA;

    // Read in size, and any hidden stuff
    s.defaultReadObject();

    // Read in capacity
    s.readInt();

    if (size > 0) {
        // be like clone(), allocate array based upon size not capacity
        ensureCapacityInternal(size);

        Object[] a = elementData;
        // Read in all elements in the proper order.
        for (int i=0; i<size; i++) {
            a[i] = s.readObject();
        }
    }
}
```

> 看完序列化，反序列化方法，我们终于又能回答开篇的第二个问题了。`elementData`之所以用`transient`修饰，是因为JDK不想将整个`elementData`都序列化或者反序列化，而只是将`size`和实际存储的元素序列化或反序列化，从而节省空间和时间。

## 创建子数组

```java
public List<E> subList(int fromIndex, int toIndex) {
    subListRangeCheck(fromIndex, toIndex, size);
    return new SubList(this, 0, fromIndex, toIndex);
}
```

我们看一下简短版的`SubList`：

```java
private class SubList extends AbstractList<E> implements RandomAccess {
    private final AbstractList<E> parent;
    private final int parentOffset;
    private final int offset;
    int size;

    SubList(AbstractList<E> parent,
            int offset, int fromIndex, int toIndex) {
        this.parent = parent;
        this.parentOffset = fromIndex;
        this.offset = offset + fromIndex;
        this.size = toIndex - fromIndex;
        this.modCount = ArrayList.this.modCount;
    }

    public E set(int index, E e) {
        rangeCheck(index);
        checkForComodification();
        E oldValue = ArrayList.this.elementData(offset + index);
        ArrayList.this.elementData[offset + index] = e;
        return oldValue;
    }

    // 省略代码...
}
```

- SubList的set()方法，**是直接修改ArrayList**中`elementData`数组的，使用中应该注意
- SubList是没有实现`Serializable`接口的，**是不能序列化的**

## 迭代器

### 创建迭代器方法

```java
public Iterator<E> iterator() {    
	return new Itr();
}
```

### Itr属性

```java
// 下一个要返回的元素的下标
int cursor;
// 最后一个要返回元素的下标 没有元素返回 -1
int lastRet = -1;
// 期望的 
modCountint expectedModCount = modCount;
```

### Itr的hasNext() 方法

```java
public boolean hasNext() {    
    return cursor != size;
}
```

### Itr的next()方法

```java
public E next() {
    checkForComodification();
    int i = cursor;
    if (i >= size)
        throw new NoSuchElementException();
    Object[] elementData = ArrayList.this.elementData;
    if (i >= elementData.length)
        throw new ConcurrentModificationException();
    cursor = i + 1;
    return (E) elementData[lastRet = i];
}

final void checkForComodification() {
    if (modCount != expectedModCount)
        throw new ConcurrentModificationException();
}
```

> 在迭代的时候，会校验`modCount`是否等于`expectedModCount`，不等于就会抛出著名的`ConcurrentModificationException`异常。什么时候会抛出`ConcurrentModificationException`？

```java
public static void main(String[] args) {
    ArrayList arrayList = new ArrayList();
    for (int i = 0; i < 10; i++) {
        arrayList.add(i);
    }
    remove(arrayList);
    System.out.println(arrayList);
}

public static void remove(ArrayList<Integer> list) {
    Iterator<Integer> iterator = list.iterator();
    while (iterator.hasNext()) {
        Integer number = iterator.next();
        if (number % 2 == 0) {
            // 抛出ConcurrentModificationException异常
            list.remove(number);
        }
    }
}
```

> 那怎么写才能不抛出`ConcurrentModificationException`？很简单，将`list.remove(number);`换成`iterator.remove();`即可。why？请看Itr的`remove()`源码…

### Itr的remove()方法

```java
public void remove() {
    if (lastRet < 0)
        throw new IllegalStateException();
    checkForComodification();

    try {
        ArrayList.this.remove(lastRet);
        cursor = lastRet;
        lastRet = -1;
        // 移除之后将modCount 重新赋值给 expectedModCount
        expectedModCount = modCount;
    } catch (IndexOutOfBoundsException ex) {
        throw new ConcurrentModificationException();
    }
}
```

原因就是因为Itr的`remove()`方法，移除之后将`modCount`重新赋值给 `expectedModCount`。这就是源码，不管单线程还是多线程，只要违反了规则，就会抛异常。

> 源码看的差不多了，开篇的问题却还剩一个！到底为什么`elementData`没有用`private`修饰呢？

我们知道的，`private`修饰的变量，内部类也是可以访问到的。难道注释中`non-private to simplify nested class access`的这句话有毛病？

当我们看表面看不到什么东西的时候，不妨看一下底层。

测试类代码：

![img]( http://qiniu.zrbac.fun/27.png)

一顿`javac`、`javap`之后（使用JDK8）：

![img]( http://qiniu.zrbac.fun/28.png)

再一顿`javac`、`javap`之后（使用JDK11）：

![img]( http://qiniu.zrbac.fun/29.png)

虽然字节码指令我还看不太懂，但是我能品出来，注释是没毛病的，`private`修饰的确会影响内部类的访问。

## ArrayList类注释翻译

类注释还是要看的，能给我们一个整体的了解这个类。我将ArrayList的类注释大概翻译整理了一下：

- ArrayList是实现`List`接口的可自动扩容的数组。实现了所有的`List`操作，允许所有的元素，包括`null`值。
- ArrayList大致和Vector相同，除了ArrayList是非同步的。
- `size` `isEmpty` `get` `set` `iterator` 和 `listIterator` 方法时间复杂度是`O(1)`，常量时间。其他方法是`O(n)`，线性时间。
- 每一个ArrayList实例都有一个`capacity`（容量）。`capacity`是用于存储列表中元素的数组的大小。`capacity`至少和列表的大小一样大。
- 如果多个线程同时访问ArrayList的实例，并且至少一个线程会修改，必须在外部保证ArrayList的同步。修改包括添加删除扩容等操作，仅仅设置值不包括。这种场景可以用其他的一些封装好的同步的`list`。如果不存在这样的`Object`，ArrayList应该用`Collections.synchronizedList`包装起来最好在创建的时候就包装起来，来保证同步访问。
- `iterator()`和`listIterator(int)`方法是`fail-fast`的，如果在迭代器创建之后，列表进行结构化修改，迭代器会抛出`ConcurrentModificationException`。
- 面对并发修改，迭代器快速失败、清理，而不是在未知的时间不确定的情况下冒险。请注意，快速失败行为不能被保证。通常来讲，不能同步进行的并发修改几乎不可能做任何保证。因此，写依赖这个异常的程序的代码是错误的，快速失败行为应该仅仅用于防止`bug`。

## 总结

- ArrayList底层的数据结构是数组
- ArrayList可以自动扩容，不传初始容量或者初始容量是`0`，都会初始化一个空数组，但是如果添加元素，会自动进行扩容，所以，创建ArrayList的时候，给初始容量是必要的
- `Arrays.asList()`方法返回的是的`Arrays`内部的ArrayList，用的时候需要注意
- `subList()`返回内部类，不能序列化，和ArrayList共用同一个数组
- 迭代删除要用，迭代器的`remove`方法，或者可以用倒序的`for`循环
- ArrayList重写了序列化、反序列化方法，避免序列化、反序列化全部数组，浪费时间和空间
- `elementData`不使用`private`修饰，可以简化内部类的访问