const initialState = {
    logged: false,
    showModal: false,
}


const reducer = (state = initialState, action) => {

    switch(action.type) {
        case "SWITCH_LOGIN_STATUS":
            return {
                ...state,
                logged: !state.logged,
            }
    }

    switch(action.type) {
        case "SWITCH_LOGIN_MODAL":
            return {
                ...state,
                showModal: !state.showModal,
            }
    }

    return state;
}


export default reducer;
