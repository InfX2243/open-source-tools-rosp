export const SAMPLE_JSONS = {
  apiResponse: JSON.stringify(
    {
      status: "success",
      code: 200,
      message: "Users retrieved successfully",
      meta: {
        totalRecords: 3,
        page: 1,
        perPage: 10,
        filters: { role: "developer", active: true }
      },
      data: [
        {
          id: "usr_9021",
          name: "Aarav Sharma",
          email: "aarav@rosp.dev",
          role: "Lead Frontend Engineer",
          skills: ["React", "JavaScript", "Vite", "CSS Modules"],
          metrics: { commits: 142, PRsReviewed: 38 },
          isVerified: true,
          lastLogin: "2026-07-31T18:42:00Z"
        },
        {
          id: "usr_9022",
          name: "Sophia Chen",
          email: "sophia@rosp.dev",
          role: "Fullstack Architect",
          skills: ["Node.js", "Python", "Docker", "GraphQL"],
          metrics: { commits: 310, PRsReviewed: 95 },
          isVerified: true,
          lastLogin: "2026-07-30T11:15:20Z"
        },
        {
          id: "usr_9023",
          name: "David Miller",
          email: "david@rosp.dev",
          role: "DevOps Specialist",
          skills: ["Kubernetes", "AWS", "Terraform", "CI/CD"],
          metrics: { commits: 88, PRsReviewed: 24 },
          isVerified: false,
          lastLogin: null
        }
      ]
    },
    null,
    2
  ),

  ecommerce: JSON.stringify(
    {
      store: "ROSP Tech Supplies",
      currency: "USD",
      cart: {
        cartId: "crt_88190",
        itemsCount: 2,
        subtotal: 149.98,
        tax: 12.00,
        total: 161.98,
        items: [
          {
            sku: "DEV-KB-001",
            title: "Custom Mechanical Keyboard",
            category: "Peripherals",
            quantity: 1,
            unitPrice: 119.99,
            inStock: true,
            tags: ["rgb", "wireless", "hot-swappable"]
          },
          {
            sku: "DEV-MAT-009",
            title: "ROSP Large Desk Mat",
            category: "Accessories",
            quantity: 1,
            unitPrice: 29.99,
            inStock: true,
            tags: ["waterproof", "stitched-edges"]
          }
        ]
      }
    },
    null,
    2
  ),

  malformed: `{
  store: 'ROSP Open Source Tools',
  tool: "JSON Formatter & Visualizer",
  features: [
    "Instant Formatting",
    "Auto Syntax Repair", // Trailing comma error!
  ],
  version: 1.0,
  isAwesome: true,
}`
};
