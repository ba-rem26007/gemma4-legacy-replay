// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #37775, validé pre/post automatiquement
// Issue: Exception is thrown when a file with .webp extension is opened from the Back Office Customer Service.
// The fix adds '.webp' to the allowed extensions list in AdminCustomerThreadsController.
const { test, expect } = require('@playwright/test');

test('opening a .webp attachment in customer service does not throw an exception', async ({ page }) => {
  // 1. Front Office: Send a contact message with a .webp attachment
  await page.goto('/contact');
  await page.fill('#email', 'customer@example.com');
  await page.fill('#subject', 'Test WebP Attachment');
  await page.fill('#message', 'Please check this webp image.');
  
  // Create a dummy webp file for upload
  await page.setInputFiles('input[type="file"]', {
    name: 'test_image.webp',
    mimeType: 'image/webp',
    buffer: Buffer.from('fake-webp-content'),
  });
  
  await page.click('#submitContact');
  
  // 2. Back Office: Navigate to Customer Service
  await page.goto('/admin-dev/');
  
  // Find the Customer Service link in the menu
  const csLink = page.locator('a:has-text("Customer Service"), a:has-text("Service client")').first();
  await csLink.click();

  // Handle the "understand the risks" security page if it appears (Symfony token issue)
  if (await page.locator('text=/comprends les risques|understand the risks/i').isVisible()) {
    await page.click('text=/comprends les risques|understand the risks/i');
  }

  // 3. Open the latest thread
  // The threads are usually in a table/grid. We click the first one.
  await page.locator('.grid-row a, .table-row a').first().click();

  // 4. Click the attachment and verify the response
  // The attachment link contains 'filename='
  const attachmentLink = page.locator('a[href*="filename="]');
  await expect(attachmentLink).toBeVisible();

  const responsePromise = page.waitForResponse(res => res.url().includes('filename='));
  await attachmentLink.click();
  const response = await responsePromise;

  // Assertion: The response should be successful (200) and NOT contain the "Invalid file extension" error
  expect(response.status()).toBe(200);
  const body = await response.text();
  expect(body).not.toContain('Invalid file extension');
});
