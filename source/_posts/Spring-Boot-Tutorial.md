---
title: Spring-Boot-Tutorial
date: 2019-12-02 14:33:35
tags: 
- Java
categories: 学习笔记
---


### IoC的基本概念

#### 依赖注入

#### 构造方法注入(constructor injection)

被注入对象可通过在其构造方法中声明依赖对象的参数列表，让外部(IoC容器)知道它需要哪些依赖对象。
```java
public NewsProvider(NewsListener newsListener,NewsPublisher newsPublisher){
    this.newsListener = newsListener;
    this.NewsPublisher = newsPublisher;
}
```

#### setter方法注入

为当前对象所依赖对象对应的属性添加setter方法，通过setter方法将相应的依赖对象设置到被注入对象中。
```java
public class NewsProvider{
    private NewsListener newsListener;
    private NewsPublisher newsPublisher;

    public NewsListener getNewsListener(){
        return newsListener;
    }
    public void setNewsListener(NewsListener newsListener){
        this.newsListener = newsListener;
    }
    public NewsPublisher getNewsPublisher(){
        return newsPublisher;
    }
    public void setNewsPublisher(NewsPublisher newsPublisher){
        this.newsPublisher = newsPublisher;
    }
}
```

#### 接口注入

被注入对象如果想要IoC Service Provider为其注入对象，就必须实现某个接口。该接口提供一个方法，用来为其注入依赖对象，IoC Service Provider最终通过这些接口来了解应该为被注入对象注入什么依赖对象。
接口注入比较死板和烦琐。

#### 三种方法比较

- 接口注入：现已不提倡使用，因为它强制被注入对象实现不必要的接口，带有侵入性。
- 构造方法注入：优点，对象在构造完成后，即可马上使用。缺点，当依赖对象比较多时，构造方法参数列表会比较长，而通过反射构造对象时，对相同类型的参数处理会比较困难，不利于维护和使用。
- setter方法注入：方法可以命名，所以setter方法注入在描述性上要比构造方法注入好，且setter方法可被继承，允许设置默认值，具有良好的IDE支持。缺点，对象无法在构造完成后马上进入就绪状态。


### IoC容器BeanFactory


