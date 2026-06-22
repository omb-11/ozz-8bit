// Lightweight WebSocket client wrapper for the web visualizer
export type StateHandler = (state: any) => void;
export type GenericHandler = (payload?: any) => void;

export default class WSClient {
  url: string;
  ws: WebSocket | null = null;
  reconnect: boolean = true;
  reconnectDelay = 1000;
  private stateHandler: StateHandler | null = null;
  private ackHandler: GenericHandler | null = null;
  private errorHandler: GenericHandler | null = null;
  private openHandler: GenericHandler | null = null;

  constructor(url: string) {
    this.url = url;
  }

  connect() {
    if (this.ws) return;
    try {
      this.ws = new WebSocket(this.url);
    } catch (err) {
      console.error('ws connect error', err);
      this._scheduleReconnect();
      return;
    }

    this.ws.onopen = () => {
      this.openHandler?.();
    };

    this.ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        if (msg.type === 'state') {
          this.stateHandler?.(msg.payload);
        } else if (msg.type === 'ack') {
          this.ackHandler?.(msg.payload);
        } else if (msg.type === 'error') {
          this.errorHandler?.(msg.message || msg.payload);
        }
      } catch (e) {
        console.error('ws parse error', e);
      }
    };

    this.ws.onclose = () => {
      this.ws = null;
      if (this.reconnect) this._scheduleReconnect();
    };

    this.ws.onerror = (ev) => {
      console.error('ws error', ev);
      this.errorHandler?.(ev);
    };
  }

  close() {
    this.reconnect = false;
    this.ws?.close();
    this.ws = null;
  }

  send(obj: any) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    this.ws.send(JSON.stringify(obj));
  }

  onState(fn: StateHandler) {
    this.stateHandler = fn;
  }

  onAck(fn: GenericHandler) {
    this.ackHandler = fn;
  }

  onError(fn: GenericHandler) {
    this.errorHandler = fn;
  }

  onOpen(fn: GenericHandler) {
    this.openHandler = fn;
  }

  private _scheduleReconnect() {
    setTimeout(() => {
      if (!this.reconnect) return;
      this.connect();
    }, this.reconnectDelay);
  }
}
