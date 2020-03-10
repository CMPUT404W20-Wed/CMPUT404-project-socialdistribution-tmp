import * as actionTypes from '../actions/actionTypes';
import updateObject from '../utility';

const initState = {
  token: null,
  error: null,
  loading: null,
  id: null,
  username: null,
};

const authStart = (state) => (
  updateObject(state, {
    error: null,
    loading: true,
  })
);


const authSuccess = (state, action) => (
  updateObject(state, {
    token: action.token,
    error: null,
    loading: false,
  })
);

const authFail = (state, action) => (
  updateObject(state, {
    error: action.error,
    loading: false,
  })
);

const authLogout = (state) => (
  updateObject(state, {
    token: null,
    id: null,
    username: null,
  })
);

const setUserData = (state, action) => (
  updateObject(state, {
    id: action.id,
    username: action.username,
  })
);

const reducer = (state = initState, action) => {
  switch (action.type) {
    case actionTypes.AUTH_START:
      return authStart(state, action);
    case actionTypes.AUTH_SUCCESS:
      return authSuccess(state, action);
    case actionTypes.AUTH_FAIL:
      return authFail(state, action);
    case actionTypes.AUTH_LOGOUT:
      return authLogout(state, action);
    case actionTypes.SET_USER:
      return setUserData(state, action);
    default:
      return state;
  }
};

export default reducer;