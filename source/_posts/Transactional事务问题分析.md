---
layout: 'n'
title: '@Transactional事务问题分析'
date: 2020-09-07 17:46:18
tags:
- Spring
categories: 学习笔记
---

## 一个@Transactional哪里来这么多坑？

[ 以下文章来源于程序员DMZ ，作者程序员DMZ ](https://mp.weixin.qq.com/s/infwcTVeEYK3RmI6I9NEog#)

**前言**

这篇文章我们来聊一聊平常工作时使用事务可能出现的一些问题（本文主要针对使用`@Transactional`进行事务管理的方式进行讨论）以及对应的解决方案

1. 事务失效
2. 事务回滚相关问题
3. 读写分离跟事务结合使用时的问题

# 事务失效

事务失效我们一般要从两个方面排查问题

## 数据库层面

数据库层面，数据库使用的存储引擎是否支持事务？默认情况下MySQL数据库使用的是Innodb存储引擎（5.5版本之后），它是支持事务的，但是如果你的表特地修改了存储引擎，例如，你通过下面的语句修改了表使用的存储引擎为`MyISAM`，而`MyISAM`又是不支持事务的

```mysql
alter table table_name engine=myisam;
```

这样就会出现“事务失效”的问题了

**「解决方案」**：修改存储引擎为`Innodb`。

<!--more-->

## 业务代码层面

业务层面的代码是否有问题，这就有很多种可能了

1. 我们要使用Spring的声明式事务，那么需要执行事务的Bean是否已经交由了Spring管理？在代码中的体现就是类上是否有`@Service`、`Component`等一系列注解

**「解决方案」**：将Bean交由Spring进行管理（添加`@Service`注解）

1. `@Transactional`注解是否被放在了合适的位置。在上篇文章中我们对Spring中事务失效的原理做了详细的分析，其中也分析了Spring内部是如何解析`@Transactional`注解的，我们稍微回顾下代码：

![img](http://qiniu.zrbac.fun/36.png)注解解析

> ❝
>
> 代码位于：`AbstractFallbackTransactionAttributeSource#computeTransactionAttribute`中
>
> ❞

也就是说，默认情况下你无法使用`@Transactional`对一个非public的方法进行事务管理

**「解决方案」**：修改需要事务管理的方法为`public`。

1. 出现了自调用。什么是自调用呢？我们看个例子

```java
@Service
public class DmzService {
 
 public void saveAB(A a, B b) {
  saveA(a);
  saveB(b);
 }

 @Transactional
 public void saveA(A a) {
  dao.saveA(a);
 }
 
 @Transactional
 public void saveB(B b){
  dao.saveB(a);
 }
}
```

上面三个方法都在同一个类`DmzService`中，其中`saveAB`方法中调用了本类中的`saveA`跟`saveB`方法，这就是自调用。在上面的例子中`saveA`跟`saveB`上的事务会失效

那么自调用为什么会导致事务失效呢？我们知道Spring中事务的实现是依赖于`AOP`的，当容器在创建`dmzService`这个Bean时，发现这个类中存在了被`@Transactional`标注的方法（修饰符为public）那么就需要为这个类创建一个代理对象并放入到容器中，创建的代理对象等价于下面这个类

```java
public class DmzServiceProxy {

    private DmzService dmzService;

    public DmzServiceProxy(DmzService dmzService) {
        this.dmzService = dmzService;
    }

    public void saveAB(A a, B b) {
        dmzService.saveAB(a, b);
    }

    public void saveA(A a) {
        try {
            // 开启事务
            startTransaction();
            dmzService.saveA(a);
        } catch (Exception e) {
            // 出现异常回滚事务
            rollbackTransaction();
        }
        // 提交事务
        commitTransaction();
    }

    public void saveB(B b) {
        try {
            // 开启事务
            startTransaction();
            dmzService.saveB(b);
        } catch (Exception e) {
            // 出现异常回滚事务
            rollbackTransaction();
        }
        // 提交事务
        commitTransaction();
    }
}
```

上面是一段伪代码，通过`startTransaction`、`rollbackTransaction`、`commitTransaction`这三个方法模拟代理类实现的逻辑。因为目标类`DmzService`中的`saveA`跟`saveB`方法上存在`@Transactional`注解，所以会对这两个方法进行拦截并嵌入事务管理的逻辑，同时`saveAB`方法上没有`@Transactional`，相当于代理类直接调用了目标类中的方法。

我们会发现当通过代理类调用`saveAB`时整个方法的调用链如下：

![img](http://qiniu.zrbac.fun/37.png)

实际上我们在调用`saveA`跟`saveB`时调用的是目标类中的方法，这种清空下，事务当然会失效。

常见的自调用导致的事务失效还有一个例子，如下：

```java
@Service
public class DmzService {
 @Transactional
 public void save(A a, B b) {
  saveB(b);
 }
 
 @Transactional(propagation = Propagation.REQUIRES_NEW)
 public void saveB(B b){
  dao.saveB(a);
 }
}
```

当我们调用`save`方法时，我们预期的执行流程是这样的

![img](http://qiniu.zrbac.fun/38.png)

也就是说两个事务之间互不干扰，每个事务都有自己的开启、回滚、提交操作。

但根据之前的分析我们知道，实际上在调用saveB方法时，是直接调用的目标类中的saveB方法，在saveB方法前后并不会有事务的开启或者提交、回滚等操作，实际的流程是下面这样的

![img](http://qiniu.zrbac.fun/39.png)

由于saveB方法实际上是由dmzService也就是目标类自己调用的，所以在saveB方法的前后并不会执行事务的相关操作。这也是自调用带来问题的根本原因：**「自调用时，调用的是目标类中的方法而不是代理类中的方法」**

**「解决方案」**：

1. 自己注入自己，然后显示的调用，例如：

   ```java
   @Service
   public class DmzService {
    // 自己注入自己
    @Autowired
    DmzService dmzService;
    
    @Transactional
    public void save(A a, B b) {
     dmzService.saveB(b);
    }
   
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void saveB(B b){
     dao.saveB(a);
    }
   }
   ```

   这种方案看起来不是很优雅

2. 利用`AopContext`，如下：

   ```java
   @Service
   public class DmzService {
   
    @Transactional
    public void save(A a, B b) {
     ((DmzService) AopContext.currentProxy()).saveB(b);
    }
   
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void saveB(B b){
     dao.saveB(a);
    }
   }
   ```

   > ❝
   >
   > 使用上面这种解决方案需要注意的是，需要在配置类上新增一个配置
   >
   > ```java
   > // exposeProxy=true代表将代理类放入到线程上下文中，默认是false
   > @EnableAspectJAutoProxy(exposeProxy = true)
   > ```
   >
   > ❞

   个人比较喜欢的是第二种方式

这里我们做个来做个小总结

## 总结

一图胜千言

![img](http://qiniu.zrbac.fun/40.png)事务失效的原因

# 事务回滚相关问题

回滚相关的问题可以被总结为两句话

1. 想回滚的时候事务却提交了
2. 想提交的时候被标记成只能回滚了（rollback only）

先看第一种情况：**「想回滚的时候事务却提交了」**。这种情况往往是程序员对Spring中事务的`rollbackFor`属性不够了解导致的。

> ❝
>
> Spring默认抛出了未检查`unchecked`异常（继承自 `RuntimeException` 的异常）或者 `Error`才回滚事务；其他异常不会触发回滚事务，已经执行的SQL会提交掉。如果在事务中抛出其他类型的异常，但却期望 Spring 能够回滚事务，就需要指定`rollbackFor`属性。
>
> ❞

对应代码其实我们上篇文章也分析过了，如下：

![img](http://qiniu.zrbac.fun/41.png)回滚代码

> ❝
>
> 以上代码位于：`TransactionAspectSupport#completeTransactionAfterThrowing`方法中
>
> ❞

默认情况下，只有出现`RuntimeException`或者`Error`才会回滚

```java
public boolean rollbackOn(Throwable ex) {
    return (ex instanceof RuntimeException || ex instanceof Error);
}
```

所以，如果你想在出现了非`RuntimeException`或者`Error`时也回滚，请指定回滚时的异常，例如：

```java
@Transactional(rollbackFor = Exception.class)
```

第二种情况：**「想提交的时候被标记成只能回滚了（rollback only）」**。

对应的异常信息如下：

```java
Transaction rolled back because it has been marked as rollback-only
```

我们先来看个例子吧

```java
@Service
public class DmzService {

 @Autowired
 IndexService indexService;

 @Transactional
 public void testRollbackOnly() {
  try {
   indexService.a();
  } catch (ClassNotFoundException e) {
   System.out.println("catch");
  }
 }
}

@Service
public class IndexService {
 @Transactional(rollbackFor = Exception.class)
 public void a() throws ClassNotFoundException{
  // ......
  throw new ClassNotFoundException();
 }
}
```

在上面这个例子中，`DmzService`的`testRollbackOnly`方法跟`IndexService`的`a`方法都开启了事务，并且事务的传播级别为`required`，所以当我们在`testRollbackOnly`中调用`IndexService`的`a`方法时这两个方法应当是共用的一个事务。按照这种思路，虽然`IndexService`的`a`方法抛出了异常，但是我们在`testRollbackOnly`将异常捕获了，那么这个事务应该是可以正常提交的，为什么会抛出异常呢？

如果你看过我之前的源码分析的文章应该知道，在处理回滚时有这么一段代码

![img](http://qiniu.zrbac.fun/42.png)rollback Only设置

在提交时又做了下面这个判断（这个方法我删掉了一些不重要的代码）

![img](http://qiniu.zrbac.fun/43.png)`commit_rollbackOnly`

可以看到当提交时发现事务已经被标记为`rollbackOnly`后会进入回滚处理中，并且unexpected传入的为true。在处理回滚时又有下面这段代码

![img](http://qiniu.zrbac.fun/44.png)抛出异常

最后在这里抛出了这个异常。

> ❝
>
> 以上代码均位于`AbstractPlatformTransactionManager`中
>
> ❞

总结起来，**「主要的原因就是因为内部事务回滚时将整个大事务做了一个`rollbackOnly`的标记」**，所以即使我们在外部事务中catch了抛出的异常，整个事务仍然无法正常提交，并且如果你希望正常提交，Spring还会抛出一个异常。

**「解决方案」**:

这个解决方案要依赖业务而定，你要明确你想要的结果是什么

1. 内部事务发生异常，外部事务catch异常后，内部事务自行回滚，不影响外部事务

> ❝
>
> 将内部事务的传播级别设置为nested/requires_new均可。在我们的例子中就是做如下修改：
>
> ```java
> // @Transactional(rollbackFor = Exception.class,propagation = Propagation.REQUIRES_NEW)
> @Transactional(rollbackFor = Exception.class,propagation = Propagation.NESTED)
> public void a() throws ClassNotFoundException{
> // ......
> throw new ClassNotFoundException();
> }
> ```
>
> ❞

虽然这两者都能得到上面的结果，但是它们之间还是有不同的。当传播级别为`requires_new`时，两个事务完全没有联系，各自都有自己的事务管理机制（开启事务、关闭事务、回滚事务）。但是传播级别为`nested`时，实际上只存在一个事务，只是在调用a方法时设置了一个保存点，当a方法回滚时，实际上是回滚到保存点上，并且当外部事务提交时，内部事务才会提交，外部事务如果回滚，内部事务会跟着回滚。

1. 内部事务发生异常时，外部事务catch异常后，内外两个事务都回滚，但是方法不抛出异常

> ❝
>
> ```java
> @Transactional
> public void testRollbackOnly() {
> try {
>    indexService.a();
> } catch (ClassNotFoundException e) {
>    // 加上这句代码
>    TransactionInterceptor.currentTransactionStatus().setRollbackOnly();
> }
> }
> ```
>
> ❞

通过显示的设置事务的状态为`RollbackOnly`。这样当提交事务时会进入下面这段代码

![img](http://qiniu.zrbac.fun/45.png)

![img](data:image/gif;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQImWNgYGBgAAAABQABh6FO1AAAAABJRU5ErkJggg==)显示回滚

最大的区别在于处理回滚时第二个参数传入的是false,这意味着回滚是回滚是预期之中的，所以在处理完回滚后并不会抛出异常。

# 读写分离跟事务结合使用时的问题

读写分离一般有两种实现方式

1. 配置多数据源
2. 依赖中间件，如`MyCat`

如果是配置了多数据源的方式实现了读写分离，那么需要注意的是：**「如果开启了一个读写事务，那么必须使用写节点」**，**「如果是一个只读事务，那么可以使用读节点」**

如果是依赖于`MyCat`等中间件那么需要注意：**「只要开启了事务，事务内的SQL都会使用写节点（依赖于具体中间件的实现，也有可能会允许使用读节点，具体策略需要自行跟DB团队确认）」**

基于上面的结论，我们在使用事务时应该更加谨慎，在没有必要开启事务时尽量不要开启。

> ❝
>
> 一般我们会在配置文件配置某些约定的方法名字前缀开启不同的事务（或者不开启），但现在随着注解事务的流行，好多开发人员（或者架构师）搭建框架的时候在service类上加上了@Transactional注解，导致整个类都是开启事务的，这样严重影响数据库执行的效率，更重要的是开发人员不重视、或者不知道在查询类的方法上面自己加上@Transactional（propagation=Propagation.NOT_SUPPORTED）就会导致，所有的查询方法实际并没有走从库，导致主库压力过大。
>
> ❞

其次，关于如果没有对只读事务做优化的话（优化意味着将只读事务路由到读节点），那么`@Transactional`注解中的`readOnly`属性就应该要慎用。我们使用`readOnly`的原本目的是为了将事务标记为只读，这样当MySQL服务端检测到是一个只读事务后就可以做优化，少分配一些资源（例如：只读事务不需要回滚，所以不需要分配undo log段）。但是当配置了读写分离后，可能会可能会导致只读事务内所有的SQL都被路由到了主库，读写分离也就失去了意义。

