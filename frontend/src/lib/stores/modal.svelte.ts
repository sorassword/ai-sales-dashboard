import { writable } from 'svelte/store';

export type ModalType =
  | 'store-detail'
  | 'employee-detail'
  | 'revenue-trend'
  | 'bot-trend'
  | 'correlation'
  | 'digest'
  | 'readiness-collection';

type ModalState = {
  open: boolean;
  type: ModalType | null;
  payload: unknown;
};

export const modalState = writable<ModalState>({
  open: false,
  type: null,
  payload: null
});

export function openModal(type: ModalType, payload: unknown) {
  modalState.set({ open: true, type, payload });
}

export function closeModal() {
  modalState.set({ open: false, type: null, payload: null });
}
