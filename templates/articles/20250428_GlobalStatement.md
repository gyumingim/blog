---
id: 27
title: "[공부] 전역 상태 관리 라이브러리 개념 정리"
subtitle: "(Recoil Jotai) (Zustand  Redux-Toolkit) (React Query)"
date: "2025.04.15"
thumbnail: ""
---
#

>⚠️ 이 블로그는 다른 사람이 보고 따라하라고 적은 게 아닌 작성자의 복기만을 위한 블로그입니다
#
전역 상태 관리 라이브러리의 특징을 Deep Dive 해보면서 바운더리 V2에 뭘 쓸지 정해봅시다
#
---
#
## Redux Toolkit Deep Dive
#
1. Redux 공식 팀이 만든, Redux 사용을 빠르고 쉽게 만들어주는 공식 추천 도구입니다.
2. 살짝 Spring - Spring Boot와 비슷한 느낌입니다
#
### Toolkit이 없는 Redux는 어땠나?
#
1. action type을 문자열로 직접 선언하고
2. action creator 함수를 별도로 만들고
3. reducer에서 switch 문을 쓰고
4. 비동기 작업은 thunk 같은 미들웨어를 직접 설정해야 했다
#
→ 버그 나기 매우 쉽고, 보일러 플레이트 코드가 상당히 많음
#
### Toolkit을 쓰면 좋은 점
#
1. action type/action creator/reducer 코드 따로따로 써야 함
    - createSlice로 한 파일에 묶기
2. 비동기 처리 설정이 복잡함
    - createAsyncThunk로 쉽게 비동기 액션 작성
3. immer 없이 직접 불변성 관리를 해야 함
    - immer 기본 내장, 직접 수정하는 것처럼 코딩 가능
4. 스토어 설정 귀찮음 (applyMiddleware, compose 등)
    - configureStore로 알아서 다 설정
5. redux-devtools 설정 귀찮음
    - 자동 devtools 연결
#
### Redux Toolkit의 주요 기능
# 
1. configureStore
    - 스토어를 쉽게 만들 수 있습니다
    - 미들웨어, devtools 세팅이 자동입니다
    

```ts
    import { configureStore } from '@reduxjs/toolkit'

    const store = configureStore({
        reducer: rootReducer,
    })
```

2. createSlice
    - action type, action creator, reducer를 한 번에 정의합니다
    

```ts
    import { createSlice } from '@reduxjs/toolkit'

    const counterSlice = createSlice({
    name: 'counter',
    initialState: 0,
    reducers: {
        increment: state => state + 1,
        decrement: state => state - 1
    }
    })

    export const { increment, decrement } = counterSlice.actions
    export default counterSlice.reducer
```

3. createAsyncThunk
    - 비동기 API 호출을 아주 간단하게 처리할 수 있습니다


```ts
    import { createAsyncThunk } from '@reduxjs/toolkit'

    export const fetchUser = createAsyncThunk('user/fetch', async (userId) => {
        const response = await fetch(`/api/user/${userId}`)
        return response.json()
    })

```

4. createEntityAdapter
    - 목록(배열) 상태 관리(ex. 사용자 리스트)에 특화된 도구입니다.
    - CRUD 작업이 깔끔해집니다.

5. RTK Query
    - GraphQL/Apollo처럼 자동 API 호출 관리를 지원하는 도구입니다.
    - 직접 thunk를 만들 필요 없이 서버 상태를 관리할 수 있습니다.
#
### Redux toolkit의 장단점
#
#### 장점
#
1. 모니터링이 쉽다
2. 대규모 커뮤니티
3. 비동기 로직 관리가 쉬워진다
#
#### 단점
#
1. 소규모 프로젝트와 맞지 않음
2. 폴더 구조 설계가 중요하다
3. RTK Query까지 쓰면 구조가 복잡해질 수 있다
#
---
#
## Zustand
#
### 장점
#
1. 스토어 정의용 create 함수 하나로 상태, 액션, 셋터를 모두 설정할 수 있습니다.
2. useStore(selector) 훅을 사용해 필요한 상태만 선택적으로 구독하고, 변경 시 해당 컴포넌트만 리렌더링됩니다.
3. 로깅, persist, undo/redo 등 미들웨어를 쉽게 추가할 수 있으며, Redux DevTools와 연동해 상태 변화를 시각화할 수 있습니다.
4. 내부적으로 Immer를 사용해 “직접 변경”하듯 코딩해도 안전하게 불변성을 보장합니다.
5. 서로 다른 모듈별로 여러 스토어를 만들거나, 하나의 전역 스토어 안에 여러 slice를 관리할 수 있습니다.
#
### 단점
#
1. Redux에 비해 서드파티 미들웨어·플러그인이 적어, 특정 기능을 직접 구현해야 할 때가 있습니다
2. 매우 복잡한 비즈니스 로직이나 대규모 상태 관리에는 패턴을 직접 설계해야 해 적합하지 않을 수 있습니다
3. Redux의 액션/리듀서 철학에 익숙한 개발자는 API가 다소 생소할 수 있습니다
4. 셀렉터나 메모이제이션을 활용해 리렌더링 범위를 직접 조절해야 합니다
#
## 사용 예시
#
store.js
```js
import create from 'zustand'

export const useCounterStore = create((set) => ({
  count: 0,
  increase: () => set((state) => ({ count: state.count + 1 })),
  reset: () => set({ count: 0 })
}))
```
#
Counter.js
```js
import React from 'react'
import { useCounterStore } from './store'

export default function Counter() {
  const { count, increase, reset } = useCounterStore((state) => ({
    count: state.count,
    increase: state.increase,
    reset: state.reset
  }))

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increase}>+1</button>
      <button onClick={reset}>Reset</button>
    </div>
  )
}
```
#
---
#
## Recoil
#
Recoil은 React 전용으로 설계된 실험적(atom/selector 기반) 상태 관리 라이브러리로, 상태를 가장 작은 단위(atom)로 분리해 세분화된 구독과 파생 상태(derived state) 계산을 지원합니다.
#
### 주요 기능
#
1. Atom & Selector
    - atom: key와 default만으로 상태 선언 
    - selector: 동기/비동기 파생 상태 계산 지원 
2. Atom/Selector 패밀리
    - atomFamily·selectorFamily: 파라미터 기반으로 동적 상태를 생성해, 반복되는 패턴의 상태 관리 간소화 
3. 비동기 및 Suspense 통합
    - 셀렉터에서 async 함수를 써서 비동기 데이터를 반환 가능하며, React Suspense와 연동해 로딩 상태를 처리할 수 있습니다 
4. useRecoilCallback
    - atom/selector에 대한 일괄 읽기·쓰기 로직을 컴포넌트 외부로 추출해 재사용할 수 있는 콜백 훅을 제공합니다 
#
### 장점
#
1. 보일러플레이트 최소화: action type·action creator 없이 atom·selector만으로 상태 관리 가능 
2. 세분화 구독: atom 단위로 구독해 필요한 컴포넌트만 리렌더링 
3. 파생 상태 관리: selector로 복잡한 파생 로직을 손쉽게 구현 
4. 동시성 지원: Concurrent Mode와 Suspense를 네이티브로 지원 
5. 비동기 통합: API 호출 같은 비동기 로직을 셀렉터에서 직접 처리 
6. 유연한 모듈화: atomFamily/selectorFamily로 반복 패턴 상태 관리 간소화
#
### 단점
#
1. 미들웨어 부재: Redux 같은 middleware 시스템이 없어, 로깅·트래킹 로직을 직접 구현해야 함 
2. 커뮤니티 규모 작음: 상대적으로 생태계와 레퍼런스가 부족해 정보 탐색이 어려울 수 있음 
3. 학습 곡선: atom/selector 개념과 Suspense 통합 사용에 익숙해지기까지 다소 시간이 필요 
4. 실험적 성격: GitHub 리포지토리가 2025년부터 읽기 전용(archived) 상태여서 장기 지원 여부 불확실 
#
### 예제
#
```js
import React, { Suspense } from 'react';
import {
  RecoilRoot,
  atom,
  selector,
  useRecoilState,
  useRecoilValue,
} from 'recoil';

// 1) Atom 정의
const textState = atom({
  key: 'textState',
  default: '',
});

// 2) Selector 정의 (동기 파생 상태)
const charCountState = selector({
  key: 'charCountState',
  get: ({ get }) => {
    const text = get(textState);
    return text.length;
  },
});

// 3) 컴포넌트
function TextInput() {
  const [text, setText] = useRecoilState(textState);
  return (
    <input
      type="text"
      value={text}
      onChange={e => setText(e.target.value)}
    />
  );
}

function CharacterCount() {
  const count = useRecoilValue(charCountState);
  return <p>Character Count: {count}</p>;
}

// 4) 앱 루트
export default function App() {
  return (
    <RecoilRoot>
      <Suspense fallback={<div>Loading...</div>}>
        <TextInput />
        <CharacterCount />
      </Suspense>
    </RecoilRoot>
  );
}
```
#
---
#
## Jotai
#
Jotai는 React 전용의 원자(atom) 기반(state atomization) 상태 관리 라이브러리로, core API가 단 2KB에 불과할 만큼 경량이며, atom·useAtom·Provider 같은 최소한의 함수만으로 상태를 선언하고 관리할 수 있습니다 
#
각 atom은 독립된 상태 단위로, selector나 atomFamily를 통해 파생(derived) 상태를 선언적으로 계산할 수 있으며, jotai/utils·jotai-tanstack-query·jotai-urql 같은 유틸리티와 확장(extension) 을 통해 로컬 저장소 연동, React Query 통합, GraphQL/URQL 연동 등 다양한 기능을 제공합니다 
#
### 주요 기능
#
- atom, useAtom, Provider 등 4가지 내외의 함수만으로 이루어진 간결한 설계 
- jotai/utils에는 atomWithStorage, splitAtom, atomWithReducer 등 상태 영속성, 리스트 분할, 리듀서 통합 등을 지원하는 유틸이 포함
- jotai-tanstack-query로 React Query 기능을 atom 레벨로 바로 사용하고, jotai-urql로 URQL(GraphQL) 연동도 가능
- jotai/vanilla를 통해 React 외부에서도 createStore/get/set/sub API로 atom을 제어할 수 있음
- jotai-devtools를 설치하면 atom별 상태 변경을 실시간으로 추적하는 UI와 훅을 제공
#
### 장점
#
- 경량 번들(2 KB): core API가 약 2KB로, 애플리케이션 번들 크기를 최소화합니다 
- 세분화된 구독: atom 단위로 구독해, 특정 atom이 바뀔 때만 관련 컴포넌트가 리렌더링되어 성능 최적화가 용이합니다 
- 직관적 API: React의 useState와 유사한 useAtom 훅 덕분에 학습 곡선이 낮습니다 
- 우수한 TypeScript 지원: generics 기반 타입 추론으로 atom을 타입 안전하게 정의할 수 있습니다 
- 광범위한 호환성: Next.js, Remix, React Native 등 다양한 React 프레임워크에서 바로 사용 가능합니다 
#
### 단점
#
- 미들웨어 부재: Redux처럼 일관된 middleware 시스템이 없어, 로깅·사이드이펙트를 위해 별도 구현이 필요합니다 
- 작은 생태계: 커뮤니티와 플러그인 수가 Redux/React Query에 비해 제한적일 수 있습니다 
- 폴더 구조 관리 필요: atom이 많아지면 파일·폴더 설계를 직접 고민해야 하며, 관리 부담이 커질 수 있습니다 
- 과도한 자유도: 파생 상태를 직접 설계해야 하므로, 복잡 로직에는 패턴 수립이 요구되며 일부에겐 부담이 될 수 있습니다 
- 추가 설정 필요: SSR이나 Concurrent Mode 통합 시, 기본 설정 외에 약간의 추가 작업이 필요할 수 있습니다 
#
### 예제 코드
#
```js
import { atom, useAtom } from 'jotai';

// 기본 atom: 숫자 상태
const countAtom = atom(0);

// 파생 atom: countAtom의 값을 두 배로
const doubleAtom = atom((get) => get(countAtom) * 2);

export function Counter() {
  const [count, setCount] = useAtom(countAtom);
  const [double] = useAtom(doubleAtom);

  return (
    <div>
      <p>Count: {count}</p>
      <p>Double: {double}</p>
      <button onClick={() => setCount(c => c + 1)}>Increment</button>
    </div>
  );
}
```
#
---
#
## React Query
#
React Query(현재는 TanStack Query)는 서버 상태 관리에 최적화된 데이터 페칭·캐싱·동기화 라이브러리로, useQuery와 useMutation 훅을 중심으로 자동 캐싱, 백그라운드 리패칭, 폴링, 의존성 쿼리, 무효화(invalidation) 같은 강력한 기능을 제공합니다. 이를 통해 API 호출 로직을 컴포넌트에서 분리하고, 네트워크 요청을 최소화해 개발 생산성과 사용자 경험을 모두 개선할 수 있습니다. 단, 과도한 쿼리 구독 시 성능 저하, 추상화로 인한 내부 메커니즘 비가시성 등의 단점도 있어, 사용 범위와 패턴을 잘 설계해야 합니다.
#
### 주요 기능
#
1. 선언적 데이터 페칭 (useQuery)
    - useQuery 훅을 사용해 키 기반(query key) 의존성을 선언하고, Promise를 반환하는 함수만 넘기면 자동으로 데이터를 가져옵니다 
2. 뮤테이션 관리 (useMutation)
    - useMutation 훅으로 POST/PUT/DELETE 같은 비동기 변경 요청을 처리하며, 성공·실패 시 후속 작업(캐시 무효화 등)을 쉽게 구성할 수 있습니다 
3. 자동 캐싱 & 무효화
    - Normalized Cache가 아닌 키-값 기반 캐싱을 제공하며, staleTime, cacheTime 등 옵션으로 캐시 유효 기간을 제어할 수 있습니다 
    - queryClient.invalidateQueries()로 특정 쿼리를 무효화해 최신 데이터를 확보합니다 
4. 백그라운드 리패칭 & 폴링
    - Window focus refetching: 탭이 다시 활성화되면 자동으로 재요청하고,
    - Polling: refetchInterval 옵션으로 주기적 갱신을 설정할 수 있습니다 
5. 의존성 쿼리 & 무한 스크롤
    - 한 쿼리 결과를 다음 쿼리의 입력으로 사용하는 Dependent Queries 지원
    - 페이지네이션/무한 스크롤용 useInfiniteQuery 훅 내장 
6. 개발자 도구 & SSR 지원
    - React Query Devtools를 통해 쿼리 상태, 캐시, 리패칭 로그를 시각화할 수 있습니다 
    - 서버 사이드 렌더링(SSR)과 하이드레이션(hydration) 패턴을 공식 지원해, 초기 로드를 빠르게 구성할 수 있습니다 
#
### 장점
#
1. 네트워크 최적화: 필요한 데이터만 요청하고, 불필요한 재요청을 방지해 모바일·로우밴드 환경에서도 효율적 

2. 보일러플레이트 감소: useEffect 내부의 fetch → setState 로직을 대체해 코드가 간결해집니다 

3. Rich UX: 낙관적 업데이트, 백그라운드 리패칭, 에러·로딩 상태 관리가 쉬워 반응성 높은 UI 구현이 용이 

4. 강력한 커뮤니티 생태계: Apollo, Relay 대비 가볍고, 다양한 프레임워크로 확장된 TanStack Query로서 활발하게 유지·관리 중 
#
### 단점
#
1. 과도한 구독 성능 저하: 수백 개의 useQuery 구독 시 렌더 성능이 떨어질 수 있음
2. 추상화의 블랙박스화: 캐시 구조나 내부 갱신 로직이 직접 보이지 않아, 디버깅·커스터마이징이 어려울 수 있음 
3. 캐싱 한계: 정교한 normalized caching은 지원하지 않아, 복잡 관계 데이터를 
효율적으로 처리하려면 추가 설계가 필요 
4. 학습 곡선: 다양한 훅 옵션과 패턴(의존성, 무효화, 하이드레이션 등)을 
이해하려면 다소 시간이 필요합니다 
#
### 간단 예시
#
```js
import React from 'react';
import { useQuery, useMutation, QueryClient, QueryClientProvider } from '@tanstack/react-query';

// 1) 쿼리 클라이언트 생성
const queryClient = new QueryClient();

function Todos() {
  // 2) 할 일 목록 불러오기
  const { data: todos, isLoading, error } = useQuery(
    ['todos'],
    () => fetch('/api/todos').then(res => res.json()),
    { staleTime: 1000 * 60 } // 1분간 신선 상태 유지
  );

  // 3) 새 할 일 추가
  const addTodo = useMutation(
    newTodo => fetch('/api/todos', { method: 'POST', body: JSON.stringify(newTodo) }),
    {
      onSuccess: () => {
        // 추가 후 목록 무효화
        queryClient.invalidateQueries(['todos']);
      }
    }
  );

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error!</p>;

  return (
    <div>
      <ul>
        {todos.map(t => <li key={t.id}>{t.title}</li>)}
      </ul>
      <button onClick={() => addTodo.mutate({ title: 'New Task' })}>
        Add Todo
      </button>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Todos />
    </QueryClientProvider>
  );
}
```
#
---
#
## 그래서 뭐씀?
#
Jotai + React Query를 쓸 것이다.
(부마위키에서도 쓰인 검증된 조합)