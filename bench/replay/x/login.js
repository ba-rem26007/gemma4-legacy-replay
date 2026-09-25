module.exports = async (page) => {
  await page.goto('/admin-dev/index.php?controller=AdminLogin');
  await page.fill('#email', 'demo@prestashop.com');
  await page.fill('#passwd', 'prestashop_demo');
  await page.click('#submit_login');
  await page.waitForURL(/AdminDashboard/);
};
