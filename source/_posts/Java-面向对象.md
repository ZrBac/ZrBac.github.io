---
title: Java-面向对象
date: 2020-05-11 09:16:26
tags:
- Java
categories: 语言基础
---

## 面向对象 

基本数据类型和引用数据类型传参的区别

Java内存空间
栈区：
- 每个线程包含一个栈区，栈中只保存基础数据类型的值和对象的引用，当一段代码或一个方法调用完毕后，栈中为这段代码提供的基本数据类型或对象的引用被立即释放。
- 每个栈中的数据(原始类型和对象引用)私有，其他栈不能访问。
- 栈分为3个部分：基本类型变量区、执行环境上下文、操作指令去(存放操作指令)。

堆区：
- 存储的都是对象，每个对象都包含一个与之对应的class信息。(class用来得到操作指令)
- Jvm只有一个堆区(heap)被所有线程共享，堆中不存放基本类型和对象引用，只存放对象本身。

方法区
- 也叫静态区，和堆一样，被所有线程共享，方法区包含所有的class和static变量。
- 方法区中包含的都是在整个程序中永远唯一的元素，如class，static变量。

![内存空间](https://user-images.githubusercontent.com/33156501/81540262-f655ec80-93a3-11ea-9879-0c45124a433c.png)
1.整数、浮点数、字符为基本数据类型。
2.字符串、数组为引用类型(内存数据的索引)。
- 基本数据类型参数的传递，是调用方值的复制，其各自的后续修改，互不影响。
- 引用数据类型参数的传递，若在方法体中修改形参指向的数据内容，则会对实参变量的数值产生影响，因为形参和实参变量共享同一块堆区。
- 当使用引用数据类型作为方法的形参时，若在方法体中修改形参变量的指向，此时不会对实参变量的数值产生影响，因为此时形参变量和实参变量分别指向不同的堆区。

<!--more-->

### 封装

将类的某些信息隐藏在类的内部，不允许外部程序直接访问，而是通过该类提供的方法来对隐藏的信息进行操作和访问。

Java中的权限修饰符：

1.公共类型public
- public可修饰类、成员变量、构造方法、方法成员。
- 被public修饰的成员，可以在任何一个类中被调用，无论同不同包。
- public是权限最大的修饰符。

2.私有类型private
- 可修饰成员变量，构造方法、方法成员，不能修饰类(不考虑内部类)。
- 被private修饰的成员，只能在定义他们的类中使用，在其他类中不能调用。

3.保护类型protect
- 可修饰成员变量，构造方法、方法成员，不能修饰类(不考虑内部类)。
- 被protected修饰的成员，能在定义它们的类中、同包的类中被调用，如果有不同包的类想调用它们，那么这个类必须是定义它们的类的子类。

4.默认类型default
- 可修饰类、成员变量、构造方法、方法成员，均可使用默认权限，即不写任何关键字。
- 默认权限即同包权限，同包权限的元素只能在定义它们的类中，以及同包的类中被调用。

**yes表示该权限修饰符所修饰的成员可被该处访问**
修饰符 | 类内部 | 同包 | 子类 | 任何地方
:-: | :-: | :-: | :-: | :-: | :-:
private | yes |
default | yes | yes |
protected | yes | yes | yes |
public  | yes | yes | yes | yes |


### 继承

继承(Inheritance)是一种联结类与类的层次模型。指的是一个类(称为子类、子接口)继承另外的一个类(称为父类、父接口)的功能，并可以增加它自己的新功能的能力，继承是类与类或者接口与接口之间最常见的关系；继承是一种is-a关系。

![继承](blog_images/继承.png)


```java
public class Main {
    public static void main(String[] args) {
        Student s = new Student("Xiao Ming", 12, 89);
    }
}

class Person {
    protected String name;
    protected int age;
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
}

class Student extends Person {
    protected int score;
    public Student(String name, int age, int score) {
        super(name,age);        //父类的构造器有参数，需要显式调用。默认时为super(),不含参数。
        this.score = score;
    }
}

```
子类是不继承父类的构造器（构造方法或者构造函数）的，它只是调用（隐式或显式）。如果父类的构造器带有参数，则必须在子类的构造器中显式地通过**super**关键字调用父类的构造器并配以适当的参数列表。如果父类构造器没有参数，则在子类的构造器中不需要使用**super**关键字调用父类构造器，系统会自动调用父类的无参构造器。


**向上转型**
```java
package com.java.starter;
 class Animal {
	public void eat() {
		System.out.println("父类的 eating...");
	}
}
class Bird extends Animal {	
	@Override
	public void eat() {
		System.out.println("子类重写的父类的  eatting...");
	}	
	public void fly() {
		System.out.println("子类新方法  flying...");
	}
}

public class Main {
	public static void main(String[] args) {
		Animal b=new Bird(); //向上转型
		b.eat(); 
		//  b.fly(); b虽指向子类对象，但此时子类作为向上的代价丢失和父类不同的fly()方法
		sleep(new Male());
		sleep(new Female()); //传入的参数是子类-----！！
	}
	
	public static void sleep(Human h) { //方法的参数是父类------！！！
 		 h.sleep();
        }
}                        
```
```java
package com.java.starter;
public class Human {
	public void sleep() {
		System.out.println("父类人类   sleep..");
	}
}
class Male extends Human {
	@Override
	public void sleep() {
		System.out.println("男人 sleep..");
	}
}
class Female extends Human {
	@Override
	public void sleep() {
		System.out.println("女人 sleep..");
	}
}
```
如上，若是不使用向上转型，那么有多少个子类就得写多少种sleep()方法。

**向下转型**
```java
package com.java.starter;
 class Fruit {
	public void myName() {
		System.out.println("我是父类  水果...");
	}
}
 
class Apple extends Fruit { 
	@Override
	public void myName() { 
		System.out.println("我是子类  苹果...");
	}
	public void myMore() {
		System.out.println("我是你的小呀小苹果~~~~~~");
	}
}
 
public class Main { 
	public static void main(String[] args) { 
		Fruit a=new Apple(); //向上转型
		a.myName();
		
		Apple aa=(Apple)a; //向下转型,编译和运行皆不会出错(正确的)
		aa.myName();//向下转型时调用的是子类的
		aa.myMore();;
		  
		Fruit f=new Fruit();
        Apple aaa=(Apple)f; //-不安全的---向下转型,编译无错但会运行会出错
  		aaa.myName();    //f是父类对象，子类的实例aaa不能指向f
  		aaa.myMore(); 
	}
}
```
向下转型指向子类对象，所以调用子类的方法。


组合(Composition)体现的是整体与部分、拥有的关系，即has-a的关系，组合通过对现有的对象进行拼装产生新的、更复杂的功能。
推荐多使用组合的形式编写代码。

**继承与组合优缺点**
 组合关系 | 继承关系
 :-: | :-: 
优点：不破坏封装，整体类与局部类之间松耦合，彼此相对独立 | 缺点：破坏封装，子类与父类之间耦合，子类依赖于父类的实现
优点：具有较好的可拓展性 | 缺点：支持扩展，但通常会增加系统结构复杂度
优点：支持动态组合，在运行时整体对象可以选择不同类型的局部对象 | 缺点：不支持动态继承，运行时子类无法选择不同的父类
优点：整体可以对局部类进行包装，封装局部类的接口，提供新接口 | 缺点：子类不能改变父类接口
缺点：整体类不能自动获得和局部类同样的接口 | 优点：子类自动继承父类接口
缺点：创建整体类的对象时，需要创建所有局部类的对象 | 优点：创建子类对象时，无需创建父类对象



### 多态
多态指，针对某个类型的方法调用，其真正执行的方法取决于运行时期实际类型的方法。
多态的三个必要条件：继承、重写、向上转型

## 接口

## 容器

## 异常

## 泛型

## 反射
Java反射机制是指在运行状态中，对于任意一个类，都能够知道这个类的所有属性和方法；对于任意一个对象，都能够调用它的任意一个方法和属性；这种动态获取信息和调用对象的方法的功能即为反射。

## 注解

## I/O

## 图形化(Swing)