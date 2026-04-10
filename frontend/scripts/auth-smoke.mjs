const BACKEND_URL =
  process.env.BACKEND_URL ?? process.env.NEXT_PUBLIC_BACKEND_URL;

const TEST_USERNAME = process.env.TEST_AUTH_USERNAME ?? "testuser";
const TEST_PASSWORD = process.env.TEST_AUTH_PASSWORD ?? "testpass123";

let cookieHeader = "";

async function request(path, init = {}) {
  const headers = new Headers(init.headers ?? {});

  if (cookieHeader) {
    headers.set("Cookie", cookieHeader);
  }

  const response = await fetch(`${BACKEND_URL}${path}`, {
    ...init,
    headers,
  });

  const setCookie = response.headers.get("set-cookie");
  if (setCookie) {
    const nextCookie = setCookie.split(";")[0];
    if (nextCookie) {
      cookieHeader = nextCookie;
    }
  }

  return response;
}

async function expectStatus(response, expected, label) {
  if (response.status !== expected) {
    let bodyText = "";

    try {
      bodyText = await response.text();
    } catch {
      bodyText = "";
    }

    throw new Error(
      `${label} failed. Expected ${expected}, got ${response.status}.${bodyText ? ` Body: ${bodyText}` : ""}`,
    );
  }
}

async function main() {
  if (!BACKEND_URL) {
    throw new Error(
      "Missing backend URL. Set BACKEND_URL or NEXT_PUBLIC_BACKEND_URL before running the auth smoke test.",
    );
  }

  console.log(`Using backend: ${BACKEND_URL}`);
  console.log(`Using test user: ${TEST_USERNAME}`);

  const beforeLogin = await request("/auth/me");
  await expectStatus(beforeLogin, 401, "Pre-login /auth/me");
  console.log("1. Pre-login /auth/me returned 401");

  const loginResponse = await request("/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username: TEST_USERNAME,
      password: TEST_PASSWORD,
    }),
  });
  await expectStatus(loginResponse, 200, "Login");

  if (!cookieHeader.includes("session_token=")) {
    throw new Error("Login succeeded but no session_token cookie was captured.");
  }
  console.log("2. Login returned 200 and session cookie was captured");

  const meResponse = await request("/auth/me");
  await expectStatus(meResponse, 200, "/auth/me after login");
  const meBody = await meResponse.json();

  if (meBody.username !== TEST_USERNAME) {
    throw new Error(
      `/auth/me returned unexpected username: ${String(meBody.username)}`,
    );
  }
  console.log(`3. /auth/me returned 200 for ${meBody.username}`);

  const logoutResponse = await request("/auth/logout", {
    method: "POST",
  });
  await expectStatus(logoutResponse, 200, "Logout");
  console.log("4. Logout returned 200");

  cookieHeader = "";

  const afterLogout = await request("/auth/me");
  await expectStatus(afterLogout, 401, "Post-logout /auth/me");
  console.log("5. Post-logout /auth/me returned 401");

  console.log("Auth smoke test passed.");
}

main().catch((error) => {
  console.error("Auth smoke test failed.");
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});
