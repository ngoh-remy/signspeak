import { test, expect } from '@playwright/test';

test.describe('SignSpeak Authentication Flow', () => {
  test('User can register, login, and access translate page', async ({ page }) => {
    // Navigate to the landing page
    await page.goto('/');

    // Check that we are on the landing page
    await expect(page.getByText(/Start Signing Now/i)).toBeVisible();

    // Click to go to translation which should redirect to login if unauthenticated
    const getStartedBtn = page.getByText(/Start Signing Now/i);
    await getStartedBtn.click();

    // We should now be on the login/register page
    await expect(page.getByRole('heading', { name: /Welcome to SignSpeak/i })).toBeVisible();

    // Switch to Register tab
    await page.getByRole('button', { name: /Register/i }).click();

    // Fill out the registration form
    // Create a unique username and email to prevent conflict with previous tests
    const timestamp = Date.now();
    await page.getByPlaceholderText('Username').fill(`testuser_${timestamp}`);
    await page.getByPlaceholderText('Email').fill(`testuser_${timestamp}@example.com`);
    await page.getByPlaceholderText('Password').fill('SecurePassword123!');

    // Submit registration
    await page.getByRole('button', { name: /Create Account/i }).click();

    // Wait for redirect to Translate page
    await expect(page).toHaveURL(/.*\/translate/);

    // Verify Translate page elements are visible
    await expect(page.getByText(/Start Camera/i)).toBeVisible();
    await expect(page.getByText(/Camera offline/i)).toBeVisible();

    // Since we provided fake media streams in playwright.config.js,
    // we can attempt to start the camera
    await page.getByRole('button', { name: /Start Camera/i }).click();

    // It should connect (or try to connect)
    // The exact text depends on language and state, but we should see Stop Camera
    await expect(page.getByRole('button', { name: /Stop Camera/i })).toBeVisible();
  });
});
