// Fixture: correct Liquid Glass usage.
// The audit should stay quiet here apart from low-confidence informational
// leads. Any HIGH-confidence finding in this file is an audit false positive.
import SwiftUI

/// A floating map control cluster: functional UI layer, above scrolling
/// content, grouped in one container, morphing with an animated state change.
struct MapControlCluster: View {
    @Namespace private var glassNamespace
    @State private var expanded = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        GlassEffectContainer(spacing: 18) {
            HStack(spacing: 12) {
                Button {
                    withAnimation(reduceMotion ? nil : .spring) { expanded.toggle() }
                } label: {
                    Label("More", systemImage: "ellipsis")
                        .labelStyle(.iconOnly)
                }
                .buttonStyle(.glass)
                .buttonBorderShape(.circle)
                .accessibilityLabel("More map options")
                .glassEffectID("toggle", in: glassNamespace)

                if expanded {
                    Button {
                        centerOnUser()
                    } label: {
                        Label("Locate", systemImage: "location.fill")
                            .labelStyle(.iconOnly)
                    }
                    .buttonStyle(.glass)
                    .buttonBorderShape(.circle)
                    .accessibilityLabel("Center on my location")
                    .glassEffectID("locate", in: glassNamespace)
                }
            }
        }
        .padding(.trailing, 16)
    }

    private func centerOnUser() { }
}

/// Toolbar items get glass automatically — nothing added here.
struct CleanToolbar: View {
    var body: some View {
        ContentView()
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done") { }
                        .buttonStyle(.glassProminent)
                }
            }
    }
}

/// Content-layer card: standard material, not glass.
struct ContentCard: View {
    var body: some View {
        VStack(alignment: .leading) {
            Text("Weekly summary").font(.headline)
            Text("You trained four times.").font(.subheadline)
        }
        .padding()
        .background(.regularMaterial, in: .rect(cornerRadius: 16))
    }
}
