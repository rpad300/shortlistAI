# 🎯 CORRIGIR STEPS - APLICAR DESIGN MODERNO

**Problema**: Steps não têm navbar, footer, nem design moderno

**Solução**: Envolver com ModernFormLayout

---

## 🔧 COMO CORRIGIR

### InterviewerStep1.tsx

**Já fiz**:
- ✅ Import ModernFormLayout
- ✅ Import SEOHead
- ✅ Import modern-forms.css

**Falta fazer**:
Envolver o return com ModernFormLayout:

```tsx
return (
  <ModernFormLayout
    title={t('interviewer.step1_title')}
    subtitle={t('interviewer.step1_subtitle')}
    step="Step 1"
    currentStep={1}
    totalSteps={7}
  >
    <SEOHead 
      title="Interviewer Step 1"
      description="Start your CV analysis"
      noindex={true}
    />
    
    <form onSubmit={handleSubmit}>
      <div className="modern-form-group">
        <label className="modern-label modern-label-required">
          {t('forms.name')}
        </label>
        <input 
          className="modern-input"
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          placeholder={t('forms.placeholders.name')}
        />
        {errors.name && <span className="modern-alert modern-alert-error">{errors.name}</span>}
      </div>

      {/* Repetir para email, phone, etc */}

      <div className="modern-form-actions">
        <button 
          type="submit" 
          className="modern-btn modern-btn-large modern-btn-full"
          disabled={loading}
        >
          {loading ? t('common.loading') : t('forms.continue')}
        </button>
      </div>
    </form>
  </ModernFormLayout>
);
```

---

## ⚡ SOLUÇÃO RÁPIDA (PARA AGORA)

Vou criar um wrapper que adiciona navbar/footer SEM mudar o código interno:

### Layout com Navbar/Footer para Steps

Criar componente que envolve steps existentes.

---

## 🚀 VOU FAZER ISTO AGORA

Vou criar um StepLayout que:
- Adiciona Navbar
- Adiciona Footer
- Adiciona Background animado
- Mantém conteúdo do step como está

**Sem quebrar nada!**

---

**Aguarde...** ⏱️


