import VerifyFlow from "@/components/VerifyFlow";

export default async function VerifyPage({ params }) {
    const { token } = await params;
    return <VerifyFlow token={token} />;
}
