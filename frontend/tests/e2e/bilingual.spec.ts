import { test, expect } from '@playwright/test';

/**
 * Spec User Story 4 / quickstart.md Scenario 5: register/login/MFA/dashboard
 * screens render fully in Arabic (RTL) or English (LTR), and the language
 * toggle is present and functional on every pre-auth screen.
 *
 * Requires a running frontend dev server (see playwright.config.ts
 * `webServer`) with `auth-service`/`tenancy-service` reachable per the
 * Vite proxy config — this suite is the CI-environment integration check
 * noted throughout the other test suites' comments; it is not runnable in
 * an environment without those live services.
 */
test.describe('Bilingual, direction-aware rendering', () => {
  test('register screen renders in English (LTR) by default', async ({ page }) => {
    await page.goto('/register');
    await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
    await expect(page.getByRole('heading', { name: 'Create your account' })).toBeVisible();
  });

  test('switching to Arabic flips layout to RTL and localizes text', async ({ page }) => {
    await page.goto('/register');
    await page.getByRole('button', { name: 'العربية' }).click();

    await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
    await expect(page.getByRole('heading', { name: 'أنشئ حسابك' })).toBeVisible();
  });

  test('language choice persists across navigation from register to login', async ({ page }) => {
    await page.goto('/register');
    await page.getByRole('button', { name: 'العربية' }).click();
    await page.goto('/login');

    await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
    await expect(page.getByRole('heading', { name: 'تسجيل الدخول' })).toBeVisible();
  });
});
