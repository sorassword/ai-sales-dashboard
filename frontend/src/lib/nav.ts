import type { Component } from 'svelte';
import { LayoutDashboard, Users, Store, Trophy, CalendarCheck } from 'lucide-svelte';

export interface NavItem {
  label: string;
  href: string;
  icon: Component;
}

export const NAV: NavItem[] = [
  { label: 'Übersicht', href: '/', icon: LayoutDashboard as unknown as Component },
  { label: 'Mitarbeiter', href: '/employees', icon: Users as unknown as Component },
  { label: 'Filialen', href: '/stores', icon: Store as unknown as Component },
  { label: 'Gamification', href: '/gamification', icon: Trophy as unknown as Component },
  { label: 'Readiness', href: '/readiness', icon: CalendarCheck as unknown as Component }
];
