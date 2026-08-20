import { PrismaClient } from './generated/client';

/**
 * Seeds two isolated tenants for local development and manual isolation
 * testing (tasks.md T056; quickstart.md Scenario 4). Run with
 * `npx ts-node prisma/seed.ts` (or `prisma db seed`) against a migrated
 * database — this does not create Postgres roles/RLS, only rows.
 */
async function main() {
  const prisma = new PrismaClient();

  const tenantA = await prisma.tenant.upsert({
    where: { domain: 'tenant-a' },
    update: {},
    create: { name: 'Tenant A (seed)', domain: 'tenant-a', status: 'active' },
  });

  const tenantB = await prisma.tenant.upsert({
    where: { domain: 'tenant-b' },
    update: {},
    create: { name: 'Tenant B (seed)', domain: 'tenant-b', status: 'active' },
  });

  // eslint-disable-next-line no-console
  console.log(JSON.stringify({ seeded: [tenantA.domain, tenantB.domain] }));
  await prisma.$disconnect();
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error(err);
  process.exit(1);
});
