---
id: 6
title: "[공부] 디자인 패턴에 대한 이해"
subtitle: "상황에 맞는 설계"
date: "2025.03.20"
thumbnail: "DesignPattern.png"
---

#
## 서론
#

럭스로보 CEO 오상훈님이 학교로 와서 강연을 해주셨다. 그냥 인생 이야기를 들려주셨는데, 매사 진심인 모습이 인상깊었다. 
나도 저런 인재가 되기 위해 CS를 갈고 닦아야겠다 마음먹고 미뤄뒀던 디자인 패턴을 공부하려고 한다

#
## 디자인 패턴
#

디자인 패턴을 사용하는 이유는, 검증된 디자인 패턴을 적용해 빠르고 쉽게 효율적인 코드를 작성할 수 있기 때문이다.
#
디자인 패턴은 3가지 구조를 가진다
#
- 콘텍스트 : 문제가 발생해, 디자인 패턴이 적용 될 수 있는 상황 
- 문제 : 패턴을 통해 해결될 필요가 있는 디자인 이슈
- 해결 : 문제를 해결하도록 설계를 구성하는 요소들과 그 요소들 사이의 관계, 책임, 협력 관계

#
### 싱글톤 패턴은 클래스의 인스턴스가 오직 하나만 생성되도록 보장한다
#
아래와 같은 상황에서 사용한다
#
- 전역적으로 접근 가능한 단일 인스턴스가 필요할 때
- 중앙 제어가 필요할 때
- 인스턴스 생성 비용이 높은 객체일 때
#
```java
public class Singleton {
    private static Singleton instance;
    
    private Singleton() {}
    
    public static Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();
        }
        return instance;
    }
}
```
#
### 팩토리 메소드 패턴은 객체 생성 로직을 서브클래스로 분리한다
#
아래와 같은 상황에서 사용한다
#
- 객체 생성 로직을 분리하여 유연성 확보가 필요할 때 
- 정확한 클래스를 알 필요 없이 인터페이스만 알면 될 때
- 코드의 결합도를 감소시켜야 할 때
#
```java
interface Product {
    void operation();
}

class ConcreteProduct implements Product {
    public void operation() {
        // 구체적인 제품 로직
    }
}

abstract class Creator {
    public abstract Product createProduct();
}

class ConcreteCreator extends Creator {
    public Product createProduct() {
        return new ConcreteProduct();
    }
}
```
#
### 빌더 패턴은 복잡한 객체를 단계별로 생성한다
#
아래와 같은 상황에서 사용한다
#
- 복잡한 객체 생성 과정을 단계별로 분리해야 할 때
- 같은 생성 과정으로 다양한 객체를 생성 할 수 있을 때
- 불완전한 객체 생성을 방지 할 때
#
```java
class Product {
    private String partA;
    private String partB;
    
    public void setPartA(String partA) {
        this.partA = partA;
    }
    
    public void setPartB(String partB) {
        this.partB = partB;
    }
}

interface Builder {
    void buildPartA();
    void buildPartB();
    Product getResult();
}

class ConcreteBuilder implements Builder {
    private Product product = new Product();
    
    public void buildPartA() {
        product.setPartA("Part A");
    }
    
    public void buildPartB() {
        product.setPartB("Part B");
    }
    
    public Product getResult() {
        return product;
    }
}

class Director {
    public void construct(Builder builder) {
        builder.buildPartA();
        builder.buildPartB();
    }
}
```
#
### 어댑터 패턴은 호환되지 않는 인터페이스를 함께 작동하도록 변환합니다
#
아래와 같은 상황에서 사용한다
#
- 호환되지 않는 인터페이스 간 협력 가능
- 기존 코드 재사용 가능
- 레거시 시스템과 신규 시스템 통합 용이
#
```java
interface Target {
    void request();
}

class Adaptee {
    public void specificRequest() {
        // 특정 기능 구현
    }
}

class Adapter implements Target {
    private Adaptee adaptee;
    
    public Adapter(Adaptee adaptee) {
        this.adaptee = adaptee;
    }
    
    public void request() {
        adaptee.specificRequest();
    }
}
```
#
### 데코레이터 패턴은 객체에 동적으로 새로운 책임을 추가한다
#
아래와 같은 상황에서 사용한다
#
- 상속 없이 객체에 동적으로 기능 추가
- 각 기능을 개별 클래스로 분리하여 단일 책임 원칙 준수
- 다양한 조합의 기능 구현 가능
#
```java
interface Component {
    void operation();
}

class ConcreteComponent implements Component {
    public void operation() {
        // 기본 기능 구현
    }
}

abstract class Decorator implements Component {
    protected Component component;
    
    public Decorator(Component component) {
        this.component = component;
    }
    
    public void operation() {
        component.operation();
    }
}

class ConcreteDecorator extends Decorator {
    public ConcreteDecorator(Component component) {
        super(component);
    }
    
    public void operation() {
        super.operation();
        addedBehavior();
    }
    
    private void addedBehavior() {
        // 추가 기능 구현
    }
}
```
#
### 옵저버 패턴은 객체 상태 변경을 다른 객체에게 알린다
#
아래와 같은 상황에서 사용한다
#
- 객체 간 느슨한 결합 구현
- 상태 변화를 여러 객체에 효율적으로 전파
- 일대다 의존성 구현
#
```java
interface Observer {
    void update(String message);
}

class ConcreteObserver implements Observer {
    public void update(String message) {
        System.out.println("Received update: " + message);
    }
}

class Subject {
    private List<Observer> observers = new ArrayList<>();
    
    public void attach(Observer observer) {
        observers.add(observer);
    }
    
    public void detach(Observer observer) {
        observers.remove(observer);
    }
    
    protected void notifyObservers(String message) {
        for (Observer observer : observers) {
            observer.update(message);
        }
    }
}

class ConcreteSubject extends Subject {
    public void doSomething() {
        // 비즈니스 로직
        notifyObservers("Something happened");
    }
}
```