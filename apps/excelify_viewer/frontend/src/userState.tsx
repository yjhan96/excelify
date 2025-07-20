/*
 * Copyright 2025 Albert Han
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { useReducer, createContext, useContext } from "react";
import type { ActionDispatch, ReactNode } from "react";
import type { Pos } from "./pos";

export interface UserState {
  pos: Pos;
  isInspecting: boolean;
}

export type UserStateAction =
  | { type: "toggleIsInspecting" }
  | { type: "setPos"; newPos: Pos }
  | { type: "setIsInspecting"; newIsInspecting: boolean }
  | { type: "reset" };

const UserStateContext = createContext<UserState | null>(null);
const UserStateDispatchContext = createContext<ActionDispatch<
  [action: UserStateAction]
> | null>(null);

export function UserStateProvider({ children }: { children: ReactNode }) {
  const [userState, dispatch] = useReducer(userStateReducer, initialState);

  return (
    <UserStateContext.Provider value={userState}>
      <UserStateDispatchContext.Provider value={dispatch}>
        {children}
      </UserStateDispatchContext.Provider>
    </UserStateContext.Provider>
  );
}

export function useUserState() {
  const userState = useContext(UserStateContext);
  if (userState === null) {
    throw new Error("UserState must be used within UserStateProvider");
  } else {
    return userState;
  }
}

export function useUserStateDispatch() {
  const dispatch = useContext(UserStateDispatchContext);
  if (dispatch === null) {
    throw new Error("UserStateDispatch must be used within UserStateProvider");
  } else {
    return dispatch;
  }
}

function userStateReducer(userState: UserState, action: UserStateAction) {
  switch (action.type) {
    case "toggleIsInspecting":
      return { ...userState, isInspecting: !userState.isInspecting };
    case "setPos":
      return { ...userState, pos: action.newPos };
    case "setIsInspecting":
      return { ...userState, isInspecting: action.newIsInspecting };
    case "reset":
      return { pos: { row: 0, col: 0 }, isInspecting: false };
    default:
      throw new Error("Unknown action");
  }
}

export const initialState: UserState = {
  pos: { row: 0, col: 0 },
  isInspecting: false,
};
