---
title: Random Notes
date: 2019-12-10 19:16:31
tags:
- random stuff
categories: 学习笔记
---

### notes

---

`抽象类`

- 如果父类方法无需实现功能，仅仅是为了定义签名，目的是让子类去覆写，那么可以把父类的方法声明为抽象方法。

- 含有抽象方法的类必须定义为抽象类，无法实例化。

- 抽象类本身被设计成只能继承，因此，抽象类可以强迫子类实现其定义的抽象方法，否则编译会报错，相当于定义了规范。

---
java新建类快捷键`ctrl` `alt` `insert`

---

`接口`

- 接口（interface）定义了纯抽象规范，一个类可以实现多个接口。
- 接口也是数据类型，适用于向上转型和向下转型。
- 接口的所有方法都是抽象方法，且不能定义实例字段，可以定义default方法。

---



```java
 * @ apiNote     : 1. 一个.java文件只能有一个public类，且这个类的类名必须与文件名保持一致
 *                 2. 一个类或者类中变量不用public，protected，private修饰的，则其作用域为整个包。
 *                 3. public修饰的可以被任何其他类访问，protected主要是作用于继承关系，子类或子类的子类可以访问。private只能在类中访问
 *                 4. 局部变量的定义应遵循最小可用原则
 *                 5. final修饰的字段无法修改，修饰的类无法继承，修饰的方法无法重写。
 *                 6. 写的时候应该先写public，再写private，因为看的时候会先关注一个类暴露给外部的字段和方法。
 */


public class oopScope    //和文件名oopScope保持一致，不然报错。
{
    
}

class Person   // 不能再用public修饰
{
    final int max_age = 110; //无法再重新赋值
    private int age;//类作用域
    public String name;

    protected void hi()  //子类无法覆写
    {
        System.out.println("Hi, "+this.name);
    }

}
```



---

```java
/*
**BigDecimal
*/

//和BigInteger类似，BigDecimal用来精确表示多位小数，源码中的实现为一个BigInteger和一个scale来实现的，前者表示数值，后者表示小数位数
import java.math.*;

public class BigDec
{
    public static void main(String[]args)
    {
        BigDecimal bd = new BigDecimal("123.456");
        System.out.println(bd.multiply(bd)); // 15241.55677489
        BigDecimal d1 = new BigDecimal("123.45");
        BigDecimal d2 = new BigDecimal("123.4500");
        BigDecimal d3 = new BigDecimal("1234500");
        System.out.println(d1.scale()); // 2,两位小数
        System.out.println(d2.scale()); // 4
        System.out.println(d3.scale()); // 0

        //通过stripTrailingZeros()方法，可以将一个BigDecimal格式化为一个相等的，但去掉了末尾0的BigDecimal
        d2 = d2.stripTrailingZeros();
        System.out.println(d2);
        //如果scale返回负数，例如，-2，表示这个数是整数，并且末尾有2个0
        BigDecimal d4 = new BigDecimal("1234500");
        System.out.println(d4.scale());

        //截断和四舍五入
        BigDecimal d5 = new BigDecimal("123.456789");
        BigDecimal d6 = d5.setScale(4,RoundingMode.HALF_UP);//四舍五入
        BigDecimal d7 = d5.setScale(4,RoundingMode.DOWN);

        //比较必须用compareTo(),使用equals不仅要求值相等，还要求scale相等，因为equals是对象类实例统一的比较方法，要求对象的实例字段相等
        BigDecimal d8 = new BigDecimal("123.456");
        BigDecimal d9 = new BigDecimal("123.45600");
        System.out.println(d8.equals(d9)); // false,因为scale不同
        System.out.println(d8.equals(d9.stripTrailingZeros())); // true,因为d2去除尾部0后scale变为2
        System.out.println(d8.compareTo(d9)); // 0
    }
}
```

存在多个catch的时候 catch的顺序十分重要：子类必须要写在前面。

```java
public static void main(String[] args) {
    try {
        process1();
        process2();
        process3();
    } catch (UnsupportedEncodingException e) {
        System.out.println("IO error");
    } catch (IOException e) {
        System.out.println("Bad encoding");
    }
}
```

---



**excel查找函数--vlookup多条件匹配**

`=VLOOKUP(条件1&条件2,if({1,0},条件1范围&条件2范围,结果范围),2,0)`

注意：

1、同时按住CTRL+SHIFT+ENTER 三键结束，因为这是数组公式；

2、条件、结果范围大小要保持一致；

操作过程如下：

![avatar](https://img-blog.csdn.net/20151225163849880?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQv/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/Center)

---

centos 系统默认启动方式更改命令

```
systemctl set-default multi-user.target //命令行模式启动
```

```
systemctl set-default graphical.target  //图形界面启动
```

---

**后端工程师**

 掌握java基础，设计模式，jvm原理，spring原理及源码，linux，mysql事务隔离与锁机制，mongodb，http/tcp，多线程，分布式架构，弹性计算架构，微服务架构，java性能优化，以及相关的项目管理等 。

追求**高并发，高可用，高性能**。

crater detection algorithms（CDAs）

orthographic projection(正射投影)

---

### Java GC: Java Garbage Collection

#### How Java GC Works

- automatic memory management
- lives in the JVM
- unreferencee objects are identified and marked as ready for gc
- then marked objects are deleted
  
#### The GC Heap  
  ![avatar](https://stackify.com/wp-content/uploads/2017/05/Java-Garbage-Collection.png)
  
  - Young Generation: newly created objects first in eden then moved to survivor space,if gc it's minor gc event.
  - Old Generation: long-lived objects moved from young generation, if gc it's major gc event.
  - Permanent Generation: metadata like classes an methods are stored here, if not used maybe gced.

---


Java 集合、数组、字符串
- size() 获取泛型集合长度
- length 获取数组长度
- length() 获取字符串长度

---

IDEA Windows快捷键
- 一键格式化代码： Ctrl + Alt + L
- 代码界面全屏切换： Ctrl +Shift + F12
- 删除一整行/选中时为剪切： Ctrl + X
- 重命名文件和变量： Shift + F6
- 多行同时编辑： 按住Alt + 鼠标左键下拉
- 跳转到指定文件： Ctrl + Shift + N
- 自动创建getter和setter： Alt + Insert
- 变量抽取： Ctrl + Alt + V
- 变量加到原文： Ctrl + Alt + N
- 快速换行跳过当前所在行代码： Shift + Enter
- 不用鼠标选中多项： Shift + ↑/↓/←/→
- 切换最近编辑窗口： Ctrl + E
- 自动移除无用引用：Ctrl + Alt + O
- 跳转到选择变量所在文件：Ctrl + B
- 复制光标所在行并将复制内容插入光标下面一行：Ctrl + D
- 快速生成for循环： object.for Enter
---

POJO: plain old java object

---


字符串equals比较，避免空指针异常
- ```java
  String str = null;
  if (str.equals("test")) {
      //*代码不会触发，因为会抛出异常
  }

  String str = null;
  if ("test".equals(str)) {
      //*正确用例，不会抛出异常
  }
  ```

时序图讲解软件推荐
visual-paradigm

---
Spring Boot
CoC: Convention over Configutation
惯例优于配置原则

---


