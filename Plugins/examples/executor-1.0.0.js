// check https://executor.dk/internalbrowser for more info
window.executor = {
    _isReady : false,
    _autoId : 10000,
    _readyCallbacks : [],
    _responseCallbacks : [],
    _inputCallbacks : [],
    _data: {
        color: "",
        bg_color: "",
        query : "",
        input : "",
        command : "",
        parameter : "",
        start_input : "",
        start_command : "",
        start_parameter : ""
    },
    onReady(callback) { // you can add callback function(s) to onReady..
        if (this._isReady) {
             callback(this);
         } else {
            this._readyCallbacks.push(callback);
         }
    },
    /*
    Example :
		executor.onReady(() => {
			alert('Hello world!');
            executor.setColors;
		});
    */
    onResponse(callback) { // If you want to listen to response events you can add your callback(s) here
        this._responseCallbacks.push(callback);
    },
    /* Returns a json rpc response
    Example :
        executor.onResponse((resp) => { 
            console.log(resp.id); 
        });
    */
    onInput(callback) { // If you want to listen to Executor input change you can add your callback(s) here
        this._inputCallbacks.push(callback);
    },
    /* Returns input (full Executor input), command (the command part of Executor input), parameter (the parameter part of Executor input)
    Example :
        executor.onInput((input, command, parameter) => {
            console.log(input); // google best movies
            console.log(command); // google
            console.log(parameter); // best movies
        });
    */

    // *********** Following functions should be called after executor.onReady have been triggered

    // helper function to match colors of Executor
    setColors : function() {
        document.body.style.color = this._data.color;
        document.body.style.backgroundColor = this._data.bg_color;
    },
	// helper function to get any parameter text that might have been entered in Executor when launching the url
	getQuery : function() {
		return this._data.query;
	},
	// helper function to get text color of Executor
	getColor : function() {
		return this._data.color;		
	},
	// helper function to get background color of Executor	
	getBGColor : function() {
		return this._data.bg_color;		
	},
    // get current Executor input, if called with true it will return the value when initialized and not the current
    getInput : function(getStart = false) { 
        return getStart===true ? this._data.start_input : this._data.input;
    },
    // get current command part of Executors input, if called with true it will return the value when initialized and not the current    
    getCommand : function(getStart = false) {
        return getStart===true ? this._data.start_command : this._data.command;
    },
    // get current parameter part of Executors input, if called with true it will return the value when initialized and not the current    
    getParameter : function(getStart = false) {
        return getStart===true ? this._data.start_parameter : this._data.parameter;
    },
    /* Set executor input, parameters:
         - inputText, set the text in Executors input field
         - hintText, set the description text in Executor (optional, default empty) 
         - inputFocus, Move focus to Executor input field (optional, default false)
         - messageId, for callback result (optional, if not provided an id will be generated)
       // note: if Executor recognize your input as something it knows, hintText will be ignored.
    */
    setExecutorInput: function (inputText, hintText, inputFocus, messageId) {
        return this.sendCommand(this.createCommand('input_set', {text : inputText, hint : hintText, focus : inputFocus}, messageId));
    },
    /* helper function that will a set Executor input to a message that Executor will not try to resolve. Parameters
         - inputText, set the text in Executors input field
         - hintText, set the description text in Executor (optional, default empty) 
         - inputFocus, Move focus to Executor input field (optional, default false)
         - messageId, for callback result (optional, if not provided an id will be generated)
    */
    showMessage: function (inputText, hintText, inputFocus, messageId) {
        return this.setExecutorInput('-> '+inputText, hintText, inputFocus, messageId);
    },    
    // Helper function to clear Executor input field
    clearExecutorInput: function () {
        return this.setExecutorInput('');
    },
    /* Open a url in Executor, parameters:
         - url, will be opened in browser, so non-url values will not work
         - dismissExecutor, hide Executor when performed (optional, default=true)
         - dismissBrowser, hide this webpage and browser from Executor when opened again (optional, default=true)
         - addToHistory, add the url to Executors history (optional, default=true)
         - messageId for callback result (optional, default empty)
       Note: if user has set Executor to auto-hide in settings, then Executor will still hide even if dismissExecutor and/or dismissBrowser is set to false. 
    */
    openUrl: function (urlToOpen, dismissExecutor = true, dismissBrowser = true, addToHistory = true, messageId) {
        return this.sendCommand(this.createCommand('open_url', {url : urlToOpen, dismiss : dismissExecutor, dismiss_browser : dismissBrowser, history : addToHistory}, messageId));
    },
    /* Run input in Executor, parameters:
         - input text to run
         - dismissBrowser, hide this webpage and browser from Executor when opened again (optional, default=true)
         - addToHistory, add the url to Executors history (optional, default=true)
         - messageId for callback result (optional, default empty)
       Note: if user has set Executor to auto-hide in settings, then Executor will still hide even if dismissExecutor and/or dismissBrowser is set to false. 
    */
    runInput: function (inputText, dismissBrowser = true, addToHistory = true, messageId) {
        return this.sendCommand(this.createCommand('input_run', {text : inputText, dismiss_browser : dismissBrowser, history : addToHistory}, messageId));
    },
    /* Hide this webpage and browser
        - messageId for callback result (optional, default empty)
    */   
    dismissBrowser: function (messageId) {
        return this.sendCommand(this.createCommand('browser_dismiss', {}, messageId));
    },
    // hide Executor
    dismissExecutor: function (messageId) {
        return this.sendCommand(this.createCommand('dismiss', {}, messageId));        
    },    
    /* Set window focus to Executor input field
        - selectAll, will select all text and put cursor at end (optional, default false)
        - setCursorAtEnd, if true will set cursor at end without any selection (optional, default false)
        - cursorPos, define at which character position the cursor should be set (optional, default ignored)
        - messageId for callback result (optional, default empty)
    */
    setFocusInput: function (selectAll = false,setCursorAtEnd = false, cursorPos = -1, messageId) {
        return this.sendCommand(this.createCommand('input_focus', {select_all : selectAll, cursor_end : setCursorAtEnd, cursor_pos : cursorPos}, messageId));
    },
    /* Set focus to internal browser
        - messageId for callback result (optional, default empty)
    */
    setFocusBrowser: function (messageId) {
        return this.sendCommand(this.createCommand('browser_focus', {}, messageId));                
    },


    // ************ Internal functions, don't call these *************

    sendCommand(data) {
       if (!data.id) {
           console.log('Error: command missing id');
           return false;
       }
       if (!data.method) {
           console.log('Error: command missing method');
           return false;
       }

       return this.sendMessage(data)===true ? data.id : false;
    },
    sendMessage: function (data) { // internal function sending data to Executor
        if (!window.chrome.webview) {
            console.log('Error: webview not found');
            return false;
        }
        window.chrome.webview.postMessage(data);
        return true;
    },
    ready: function () { // executor will call this on initialization, you should hook into the onReady event though
        this._isReady = true;
        this._readyCallbacks.forEach(callback => callback(this));
        this._readyCallbacks = [];
    },

    response: function (rpc) { // internal function to handle response
        this._responseCallbacks.forEach(callback => callback(JSON.parse(rpc)));
    },
    input: function (input, command, parameter) { // internal function to handle response
        this._data.input = input;
        this._data.command = command;
        this._data.parameter = parameter;
        this._inputCallbacks.forEach(callback => callback(input, command, parameter));
    },
    createCommand : function(f_method, f_params, f_id) {
        if (f_id===undefined) { // generate an id if none is provided.
            this._autoId++;
            f_id = this._autoId;
        } 
        return {method : f_method, params : f_params, id : f_id};
    }
}